<h1 align="center"><strong>Burplist</strong></h1>

<p align="center">
  <img width="300" height="300" src="https://media.giphy.com/media/3o85xjSETVG3OpPyx2/giphy.gif">
</p>
<br />

[![CI](https://github.com/ngshiheng/burplist/actions/workflows/ci.yml/badge.svg)](https://github.com/ngshiheng/burplist/actions/workflows/ci.yml)
[![CD](https://github.com/ngshiheng/burplist/actions/workflows/cd.yml/badge.svg)](https://github.com/ngshiheng/burplist/actions/workflows/cd.yml)

## Context

Welcome to the official web crawler repository for [Burplist](https://burplist.me) built using [Scrapy](https://scrapy.org/).

Growing up in a frugal family, I would spend hours browsing online, looking for the best bang for my bucks. Needless to say, the process was super exhausting and slowly turns into frustration.

So then I thought, why not just create a search engine for craft beers?

[Read more...](https://jerrynsh.com/how-i-built-burplist-for-free/).

## Disclaimer

This software is only used for research purposes, users must abide by the relevant laws and regulations of their location, please do not use it for illegal purposes. The user shall bear all the consequences caused by illegal use.

## Features

-   [x] 10+ unique [spiders](./burplist/spiders/) for top craft beer sites in Singapore
-   [x] [Sentry](https://sentry.io/) integration
-   [x] [ScrapeOps](https://scrapeops.io) integration
-   [x] [Scraper API](https://www.scraperapi.com/?fp_ref=jerryng) for proxy requests
-   [x] Automated random user agent rotation
-   [x] Colored logging
-   [x] Data deduplication pipeline
-   [x] Database migration with [Alembic](https://alembic.sqlalchemy.org/en/latest/)
-   [x] Delayed requests middleware

## Requirements

-   [python](https://www.python.org/downloads/)
-   [pip](https://pip.pypa.io/en/stable/installation/)
-   [poetry](https://python-poetry.org/docs/#installation)
-   [docker](https://docs.docker.com/get-docker/)

## Usage

Check out [this documentation](docs/USAGE.md) on how to use.

## Contributing

For guidance on setting up a development environment and how to make a contribution, see the [contributing guidelines](docs/CONTRIBUTING.md).

## References

### List of awesome Scrapy libraries

-   https://github.com/croqaz/awesome-scrapy
-   https://github.com/groupbwt/scrapy-boilerplate

### Docker

-   https://stackoverflow.com/questions/60340228/how-to-connect-to-postgres-created-with-docker-compose-from-outside-host
-   https://stackoverflow.com/questions/50983177/how-to-connect-to-postgresql-using-docker-compose/52543774
-   https://stackoverflow.com/questions/30063907/using-docker-compose-how-to-execute-multiple-commands
