.PHONY: all
all:
	skaffold build --file-output=tags.json

.PHONY: deploy
deploy:
	skaffold deploy --build-artifacts=tags.json

.PHONY: proxy
proxy:
	gcloud run services proxy llmbench-chat \
		--project shikanime-studio-labs \
		--region us-central1

proxy-%:
	gcloud run services proxy llmbench-chat \
		--project shikanime-studio-labs \
		--region us-central1 \
		--tag $*
