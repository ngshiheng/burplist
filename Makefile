NAME := burplist
POETRY := $(shell command -v poetry 2> /dev/null)
DOCKER := $(shell command -v docker 2> /dev/null)

ifdef ENVIRONMENT
	ENVIRONMENT := $(ENVIRONMENT)
else
	ENVIRONMENT := development
	PG_HOST := $(shell docker inspect -f '{{range.NetworkSettings.Networks}}{{.Gateway}}{{end}}' dpostgres)
endif

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Welcome to $(NAME) ($(ENVIRONMENT))."
	@echo "Use 'make <target>' where <target> is one of:"
	@echo ""
	@echo "  install	install packages and prepare environment"
	@echo "  clean		clean all local cache"
	@echo "  lint		run the code linters"
	@echo "  build		build docker image for $(NAME)"
	@echo "  run		run $(NAME) in docker"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."

install:
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install --no-root

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf .scrapy

.PHONY: lint
lint:
	$(POETRY) run flake8 --statistics --show-source

build:
	$(DOCKER) build -t $(NAME) . --build-arg ENVIRONMENT=$(ENVIRONMENT)

.PHONY: run
run:
	$(DOCKER) stop $(NAME) || true && $(DOCKER) rm $(NAME) || true
	$(DOCKER) run -d -e PG_HOST=$(PG_HOST) --name $(NAME) $(NAME)
