<h1 align="center"><strong>Burplist</strong></h1>

<p align="center">
  <img width="300" height="300" src="https://media.giphy.com/media/3o85xjSETVG3OpPyx2/giphy.gif">
</p>
<br />

## Introduction

The official web crawlers repository for [Burplist](https://burplist.me) built using [Scrapy](https://scrapy.org/).

> Growing up in a frugal family, I would spend hours browsing online, looking for the best bang for my bucks. Needless to say, the process was super exhausting and slowly turns into frustration. So then I thought, why not just create a search engine for craft beers?

I have documented some of my thought process and engineering decisions while creating Burplist [here](https://jerrynsh.com/how-i-built-burplist-for-free/). Enjoy!

---

## Requirements

- [python](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [poetry](https://python-poetry.org/docs/#installation)
- Optional: [docker](https://docs.docker.com/get-docker/)

## Development

Skip to the [Usage](#usage) `docker-compose` section if you only want to try it out locally.

### Installation

```sh
poetry install

# Optional: to install dependencies only
poetry install --no-root
```

### Updating dependencies

```sh
# Optional
poetry update
```

### Setup pre-commit Hooks

[pre-commit hooks](https://pre-commit.com/index.html#installation) should already be installed after the installation step above.

Some example useful invocations:

- `pre-commit install`: Default invocation. Installs the pre-commit script alongside any existing git hooks.
- `pre-commit install --install-hooks --overwrite`: Idempotently replaces existing git hook scripts with pre-commit, and also installs hook environments.

### Database migration

This is not needed for fresh installation. You would only need this if you update any database models.

For database migration steps, please read [this](alembic/README.md).

### Setting up a database

Instructions to set up a database with Docker. Feel free to skip this step if you intend to use `docker-compose`.

However, if you intend to work on development work, setting this up would be worthwhile.

1. To spin up a `postgres` Docker container:

   ```sh
   docker run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest
   ```

2. To start the PostgreSQL Docker container, simply use `docker start dpostgres`

3. To run `psql`, do `docker exec -it dpostgres psql -U postgres`

4. Create a database name as `burplist` using `CREATE DATABASE burplist;`

---

## Usage

### List all available spiders

```sh
poetry run scrapy list
```

### Using `docker-compose`

This step builds and runs the Burplist `scrapy` application along with a `postgres` Docker container.

This is perfect for users who simply wants to try out the application locally.

```sh
# To build and start scraping with all available spiders
docker-compose up -d --build

# To run all available spiders after build
docker start burplist_scrapy
```

### Run single spider

```sh
# To run a single spider
poetry run scrapy crawl thirsty

# To run single spider with json output
poetry run scrapy crawl coldstorage -o coldstorage.json
```

### Run all spiders

```sh
poetry run scrapy list | xargs -n 1 poetry run scrapy crawl


```

### Run all spiders, in parallel

```sh
poetry shell
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

### To run on Heroku

```sh
# Optional
heroku run scrapy list | xargs -n 1 heroku run scrapy crawl
```

---

## Proxy and Sentry

This section is optional.

We use [ScraperAPI](https://www.scraperapi.com/) as our proxy server provider.

```sh
# Optional
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
export SENTRY_DSN="YOUR_SENTRY_DSN"
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Steps

1. Fork this
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Please make sure you have installed the `pre-commit` hook and make sure it passes all the lint and format check
4. Commit your changes (`git commit -am 'feat: Add some fooBar'`, make sure that your commits are [semantic](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716))
5. Push to the branch (`git push origin feature/fooBar`)
6. Create a new Pull Request

---

## References

### List of awesome Scrapy libraries

- https://github.com/croqaz/awesome-scrapy
- https://github.com/groupbwt/scrapy-boilerplate

### Docker

- https://stackoverflow.com/questions/60340228/how-to-connect-to-postgres-created-with-docker-compose-from-outside-host
- https://stackoverflow.com/questions/50983177/how-to-connect-to-postgresql-using-docker-compose/52543774
- https://stackoverflow.com/questions/30063907/using-docker-compose-how-to-execute-multiple-commands
