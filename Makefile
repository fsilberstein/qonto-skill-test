.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r"^([a-zA-Z_-]+):.*?## (.*)$$", line)
	if match:
		target, help = match.groups()
		print(f"{target:30} {help}")
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

.PHONY: help
.DEFAULT_GOAL := help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: install
install: ## Install python dependencies with poetry
	poetry install

.PHONY: regenerate-requirements
regenerate-requirements: ## Regenerate requirements.txt using poetry
	poetry export --without-hashes --output requirements.txt

.PHONY: generate-sdist
generate-sdist: ## Generate sdist of app package
	poetry build -qn

.PHONY: build-linux
build-linux: regenerate-requirements generate-sdist ## Build docker image
	docker build --rm \
		-f Dockerfile \
		-t kafka-to-dwh \
		--platform linux/amd64 \
		--build-arg PKG_SDIST=kafka_to_dwh-${PKG_VERSION}.tar.gz \
		.

.PHONY: build
build: regenerate-requirements generate-sdist ## Build docker image
	docker build --rm \
		-f Dockerfile \
		-t kafka-to-dwh \
		--build-arg PKG_SDIST=kafka_to_dwh-${PKG_VERSION}.tar.gz \
		.

.PHONY: push
push: build ## push docker image to docker hub
	docker tag kafka-to-dwh fsilberstein/kafka-to-dwh:${PKG_VERSION}
	docker tag kafka-to-dwh fsilberstein/kafka-to-dwh:latest
	docker push --all-tags fsilberstein/kafka-to-dwh

.PHONY: test
test: ## Run unit tests
	poetry run python -m unittest discover --start-directory tests/ --verbose

.PHONY: run-locally
run-locally: ## Run the pipeline locally using DirectRunner
	poetry run python main.py \
	--runner DirectRunner \
	--dev true \
	--broker localhost:9092 \
	--streaming