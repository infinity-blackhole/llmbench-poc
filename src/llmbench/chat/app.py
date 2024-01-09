import asyncio
import os

import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.globals import set_debug, set_verbose
from langchain.llms.vertexai import VertexAI
from langchain.memory.buffer import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMessageHistory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain_vertexai_extended.llms import VertexAIModelGardenPeft

from llmbench.langchain.callbacks.streamlit import \
    StreamlitRetrievalCallbackHandler


@st.cache_resource
def get_llm(model_id: str):
    if model_id == "PaLM":
        return VertexAI(
            project=os.environ["VERTEXAI_SEARCH_PROJECT_ID"],
            model_name="text-unicorn",
            max_output_tokens=512,
            streaming=True,
        )
    if model_id == "LLaMa":
        endpoint_id = os.environ["VERTEXAI_LLAMA_ENDPOINT_ID"]
    elif model_id == "Falcon":
        endpoint_id = os.environ["VERTEXAI_FALCON_ENDPOINT_ID"]
    else:
        raise ValueError(f"Unknown LLM {model_id}")
    return VertexAIModelGardenPeft(
        project=os.environ["VERTEXAI_SEARCH_PROJECT_ID"],
        endpoint_id=endpoint_id,
        max_length=1024,
        streaming=True,
    )


@st.cache_resource
def get_retriever():
    return GoogleVertexAISearchRetriever(
        project_id=os.environ["VERTEXAI_SEARCH_PROJECT_ID"],
        location_id=os.environ["VERTEXAI_SEARCH_DATA_STORE_LOCATION"],
        data_store_id=os.environ["VERTEXAI_SEARCH_DATA_STORE_ID"],
        get_extractive_answers=True,
    )


def get_chain(model_id: str, chat_memory: BaseChatMessageHistory):
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=chat_memory,
        return_messages=True,
    )
    return ConversationalRetrievalChain.from_llm(
        get_llm(model_id),
        retriever=get_retriever(),
        memory=memory,
    )


def run():
    st.set_page_config(page_title="LLM Bench Chat", page_icon="🐬")
    st.title("🐬 LLM Bench Chat")

    model_id = st.sidebar.selectbox("Select a Model", ["PaLM", "LLaMa", "Falcon"])
    msgs = StreamlitChatMessageHistory()
    chain = get_chain(model_id, msgs)

    if len(msgs.messages) == 0 or st.sidebar.button("Clear message history"):
        msgs.clear()
        msgs.add_ai_message("Hello I'm the LLM Bench Chatbot! How can I help you?")

    avatars = {"human": "user", "ai": "assistant"}
    for msg in msgs.messages:
        st.chat_message(avatars[msg.type]).write(msg.content)

    if user_query := st.chat_input(placeholder="Ask me anything!"):
        st.chat_message("user").write(user_query)

        with st.chat_message("assistant"):
            callbacks = [StreamlitRetrievalCallbackHandler(st.container())]
            response = chain(user_query, callbacks=callbacks)
            st.markdown(response["answer"])


if __name__ == "__main__":
    if os.environ.get("DEBUG", "False") == "1":
        set_debug(True)
        set_verbose(True)

    # Set Event Loop for async LLMs
    asyncio.set_event_loop(asyncio.new_event_loop())

    # Start rendering UI
    run()
