# Usage

- [Usage](#usage)
  - [List all available spiders](#list-all-available-spiders)
  - [Using `docker-compose`](#using-docker-compose)
  - [Run single spider](#run-single-spider)
  - [Run all spiders](#run-all-spiders)
  - [Run all spiders, in parallel](#run-all-spiders-in-parallel)
  - [Optional: Integrations](#optional-integrations)

## List all available spiders

```sh
poetry run scrapy list
```

## Using `docker-compose`

This step builds and runs the Burplist `scrapy` application along with a `postgres` Docker container.

This is perfect for users who simply wants to try out the application locally.

```sh
# To build and start scraping with all available spiders
docker-compose up -d --build

# To run all available spiders after build
docker start burplist_scrapy
```

## Run single spider

```sh
# To run a single spider
poetry run scrapy crawl thirsty

# To run single spider with json output
poetry run scrapy crawl coldstorage -o coldstorage.json
```

## Run all spiders

```sh
poetry run scrapy list | xargs -n 1 poetry run scrapy crawl
```

## Run all spiders, in parallel

```sh
poetry shell
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

## Optional: Integrations

[ScraperAPI](https://www.scraperapi.com/?fp_ref=jerryng) is used as our proxy server provider.
[Sentry](https://sentry.io/) is used for error monitoring.
[ScrapeOps](https://scrapeops.io) is used for job monitoring.

```sh
export SENTRY_DSN="<YOUR_SENTRY_DSN>"
export SCRAPER_API_KEY="<YOUR_SCRAPER_API_KEY>"
export SCRAPEOPS_API_KEY="<YOUR_ SCRAPEOPS_API_KEY>"
```
