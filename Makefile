IMAGE_NAME=pr-ranker

build:
	docker build -t $(IMAGE_NAME) .

exec:
	export $(shell grep -v '^#' .envrc | xargs) && \
	docker run --rm -e GITHUB_TOKEN=$$GITHUB_TOKEN -v $(PWD)/main.py:/app/main.py -v $(PWD)/.envrc:/app/.envrc -it $(IMAGE_NAME)
