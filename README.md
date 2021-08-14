<h1 align="center"><strong>Burplist</strong></h1>

<p align="center">
  <img width="300" height="300" src="https://media.giphy.com/media/3o85xjSETVG3OpPyx2/giphy.gif">
</p>
<br />

> Collect all the available beers (preferably craft beers 🍻) data in Singapore into a single place so that users can easy compare prices across different vendors and shops.

## Installation

Make sure you have [poetry](https://python-poetry.org/docs/#installation) installed on your machine.

```sh
poetry install

# Installing dependencies only
poetry install --no-root

# Updating dependencies to their latest versions
poetry update
```

## Setup Pre-commit Hooks

Before you begin your development work, make sure you have installed [pre-commit hooks](https://pre-commit.com/index.html#installation).

Some example useful invocations:

-   `pre-commit install`: Default invocation. Installs the pre-commit script alongside any existing git hooks.
-   `pre-commit install --install-hooks --overwrite`: Idempotently replaces existing git hook scripts with pre-commit, and also installs hook environments.

## Database

-   Make sure you have a running instance of the latest PostgreSQL in your local machine.

```sh
# Example to spin up a PostgreSQL Docker instance locally
docker run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest
```

-   By default, the database for this project should be named as `burplist`.
-   For database migration steps, please read [this](alembic/README.md).

---

## Start Crawling

### Run single spider

```sh
# To list all spiders
poetry run scrapy crawl list

# To run a single spider
poetry run scrapy crawl fairprice

# To run single spider with json output
poetry run scrapy crawl coldstorage -o coldstorage.json
```

### Run all spiders

```sh
poetry run scrapy list | xargs -n 1 poetry run scrapy crawl

# Run on Heroku
heroku run scrapy list | xargs -n 1 heroku run scrapy crawl
```

### Run all spiders, in parallel

```sh
poetry shell
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

---

## Using Proxy

We use [ScraperAPI](https://www.scraperapi.com/) as our proxy server provider.

```sh
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
```
