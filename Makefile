NAME := burplist
ENVIRONMENT ?= development

SHELL=/bin/bash
POETRY := $(shell command -v poetry 2> /dev/null)
DOCKER := $(shell command -v docker 2> /dev/null)

.DEFAULT_GOAL := help
##@ Helper
.PHONY: help
help:	## display this help message.
	@echo "Welcome to $(NAME) [$(ENVIRONMENT)]."
	@awk 'BEGIN {FS = ":.*##"; printf "Use make \033[36m<target>\033[0m where \033[36m<target>\033[0m is one of:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


##@ Development
.PHONY: dev
dev:	## install packages and prepare environment with poetry.
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	@$(POETRY) install
	@$(POETRY) run pre-commit install
	@$(POETRY) shell
	@echo "Done."

.PHONY: setupdb
setupdb: ## setup postgres in docker.
	@if [ -z $(DOCKER) ]; then echo "Docker could not be found. See https://docs.docker.com/get-docker/"; exit 2; fi
	@docker stop dpostgres || true && docker rm dpostgres || true
	@$(DOCKER) start dpostgres 2>/dev/null || $(DOCKER) run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest
	@timeout 30s bash -c "until docker exec dpostgres pg_isready; do sleep 5; done"
	@$(DOCKER) exec -i dpostgres psql -U postgres  <<< "CREATE DATABASE burplist;"
	@echo "Done."


##@ Usage
.PHONY: build
build:	## build docker image.
	@$(DOCKER) build -t $(NAME) . --build-arg ENVIRONMENT=$(ENVIRONMENT)
	@echo "Done."

.PHONY: run
run:	## run all spiders
	@$(POETRY) run scrapy list | xargs -n 1 poetry run scrapy crawl
	@echo "Done."

.PHONY: run-docker
run-docker:	## run all spiders using docker.
	PG_HOST := $(shell docker inspect -f '{{range.NetworkSettings.Networks}}{{.Gateway}}{{end}}' dpostgres)
	@$(DOCKER) stop $(NAME) || true && $(DOCKER) rm $(NAME) || true
	@$(DOCKER) run -d -e PG_HOST=$(PG_HOST) --name $(NAME) $(NAME)
	@echo "Done."


##@ Contributing
.PHONY: clean
clean:	## clean all local cache.
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf .scrapy

.PHONY: pr
pr:	## run tests & code linters with pre-commit.
	@$(POETRY) run pre-commit
	@echo "Done."
