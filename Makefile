NAME := burplist
SHELL=/bin/bash
POETRY := $(shell command -v poetry 2> /dev/null)
DOCKER := $(shell command -v docker 2> /dev/null)

ENVIRONMENT ?= development
PG_HOST := $(shell docker inspect -f '{{range.NetworkSettings.Networks}}{{.Gateway}}{{end}}' dpostgres)

.DEFAULT_GOAL := help

.PHONY: help
help:	## display this help message
	@echo "Welcome to $(NAME) ($(ENVIRONMENT))!"
	@awk 'BEGIN {FS = ":.*##"; printf "Use make \033[36m<target>\033[0m where \033[36m<target>\033[0m is one of:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: install
install:	## install packages and prepare environment
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	@$(POETRY) install --no-root

.PHONY: clean
clean:	## clean all local cache
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf .scrapy

.PHONY: lint
lint:	## run the code linters
	@$(POETRY) run flake8 --statistics --show-source

.PHONY: build
build:	## build docker image for burplist
	@$(DOCKER) build -t $(NAME) . --build-arg ENVIRONMENT=$(ENVIRONMENT)

.PHONY: run
run:	## run all spiders
	@$(POETRY) run scrapy list | xargs -n 1 poetry run scrapy crawl

.PHONY: run-docker
run-docker:	## run all spiders using docker
	@$(DOCKER) stop $(NAME) || true && $(DOCKER) rm $(NAME) || true
	@$(DOCKER) run -d -e PG_HOST=$(PG_HOST) --name $(NAME) $(NAME)
