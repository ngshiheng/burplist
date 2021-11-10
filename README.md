<h1 align="center"><strong>Burplist</strong></h1>

<p align="center">
  <img width="300" height="300" src="https://media.giphy.com/media/3o85xjSETVG3OpPyx2/giphy.gif">
</p>
<br />

## What is this?

This is the web crawlers repository of https://burplist.me built using Scrapy.

The site serves as a search engine for craft beers in Singapore, providing craft beer lovers pricing information for their favorite beer.

---

## Development

Make sure you have [poetry](https://python-poetry.org/docs/#installation) and [docker](https://www.docker.com/) installed on your machine.

### Installation

```sh
poetry install

# Optional: Installing dependencies only
poetry install --no-root

# Optional: Updating dependencies to their latest versions
poetry update
```

### Setup pre-commit Hooks

Before you begin your development work, make sure you have installed [pre-commit hooks](https://pre-commit.com/index.html#installation).

Some example useful invocations:

-   `pre-commit install`: Default invocation. Installs the pre-commit script alongside any existing git hooks.
-   `pre-commit install --install-hooks --overwrite`: Idempotently replaces existing git hook scripts with pre-commit, and also installs hook environments.

### Database

For database migration steps, please read [this](alembic/README.md). You would only need this if you update any database models. Not needed for fresh installation.

-   To spin up a PostgreSQL Docker instance locally

    ```sh
    docker run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest
    ```

-   To start the PostgreSQL Docker container, simply use `docker start dpostgres`.
-   To run `psql`, do `docker exec -it dpostgres psql -U postgres`
-   Create a database name as `burplist` using `CREATE DATABASE burplist;`

### Build a Burplist docker image

_NOTE: Set `PG_HOST=172.17.0.1` because that is the IP address gateway of container_

```sh
docker build -t burplist .
```

---

## Usage

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

# Optional: Run on Heroku
heroku run scrapy list | xargs -n 1 heroku run scrapy crawl
```

### Run all spiders, in parallel

```sh
poetry shell
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

### Run all spiders with Docker

1. Make sure you have a running instance of the latest PostgreSQL in your local machine (refer to the steps above)
2. Run `docker run --name burplist burplist`

---

## Proxy

We use [ScraperAPI](https://www.scraperapi.com/) as our proxy server provider.

```sh
# Optional:
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Steps

1. Fork this
2. Create your feature branch (git checkout -b feature/fooBar)
3. Please make sure you have installed the pre-commit hook and make sure it passes all the lint and format check
4. Commit your changes (git commit -am 'Add some fooBar')
5. Push to the branch (git push origin feature/fooBar)
6. Create a new Pull Request

---

## References

List of awesome Scrapy libraries

-   https://github.com/croqaz/awesome-scrapy
-   https://github.com/groupbwt/scrapy-boilerplate
