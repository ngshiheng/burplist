FROM python:3.9-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.10 \
    POETRY_NO_INTERACTION=1 \
    PG_HOST=172.17.0.1
WORKDIR /app

FROM python-base as build-base
RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

FROM build-base as final-build
COPY . .
CMD poetry run scrapy list | xargs -n 1 poetry run scrapy crawl
