ARG PYTHON_VERSION=3.9

FROM python:${PYTHON_VERSION}-slim AS base
ARG POETRY_VERSION=1.1.15
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=60 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=${POETRY_VERSION}
WORKDIR /app

FROM base AS builder
ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}
RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml /app
COPY poetry.lock /app
RUN poetry install --no-root \
    $(if [ "$ENVIRONMENT" = 'production' ]; then echo '--no-dev'; fi) \
    --no-interaction --no-ansi

FROM builder AS app
COPY . .
CMD ["sh", "-c", "poetry run scrapy list | xargs -n 1 poetry run scrapy crawl"]
