# Use a base image with Python 3.11 for building the application
FROM python:3.11-slim-buster AS base

# Install Git
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y git

# Create a non-root user
RUN useradd -m llmbenchchat

# Set the working directory
WORKDIR /home/llmbenchchat/llmbenchchat

# Set the ownership of the working directory to the non-root user
RUN chown -R llmbenchchat:llmbenchchat /home/llmbenchchat/llmbenchchat

FROM base AS build

# Switch to the non-root user
USER llmbenchchat

# Create cache directories
RUN mkdir -p /home/llmbenchchat/.cache/pip /home/llmbenchchat/.cache/pdm

# Install pdm
RUN --mount=type=cache,target=/home/llmbenchchat/.cache/pip \
    --mount=type=cache,target=/home/llmbenchchat/.cache/pdm \
    pip install --user pdm

# Copy the dependencies file
COPY pyproject.toml pdm.lock ./

# Copy the application code
COPY --chown=llmbenchchat:llmbenchchat src src
COPY --chown=llmbenchchat:llmbenchchat README.md ./

# Install the dependencies
RUN --mount=type=cache,target=/home/llmbenchchat/.cache/pip \
    --mount=type=cache,target=/home/llmbenchchat/.cache/pdm \
    /home/llmbenchchat/.local/bin/pdm sync --prod --no-editable

# Use a lightweight base image
FROM base

# Switch to the non-root user
USER llmbenchchat

# Retrieve application
COPY --from=build --chown=llmbenchchat:llmbenchchat \
    /home/llmbenchchat/llmbenchchat /home/llmbenchchat/llmbenchchat

# Expose the default Streamlit port
EXPOSE 8501

# Set the entrypoint command
COPY --chown=llmbenchchat:llmbenchchat \
    docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Set the default command
CMD ["streamlit", "run", "src/llmbench/chat/app.py", "--server.address=0.0.0.0"]
