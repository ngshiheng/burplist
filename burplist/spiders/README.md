# Debugging and Development

## Database Set Up
```sh
# To spin up a PostgreSQL Docker container
docker run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest

# To run `psql` in the Docker container
docker exec -it dpostgres psql -U postgres
```

## XPath Quick Guide

> “XPath is a language for addressing parts of an XML document”

-   https://dev.to/masihurmaruf/locator-strategy-xpath-54p7
-   https://docs.scrapy.org/en/xpath-tutorial/topics/xpath-tutorial.html

## Selecting Dynamically-loaded Content

-   https://docs.scrapy.org/en/latest/topics/dynamic-content.html
-   https://www.zyte.com/blog/handling-javascript-in-scrapy-with-splash/

```sh
docker run -d -p 8050:8050 scrapinghub/splash
```

## Using `scrapy-splash` with `scrapy shell`

```sh
pipenv run scrapy shell 'http://localhost:8050/render.html?url=https://www.alcoholdelivery.com.sg/beer-cider/craft-beer'
```

## To Check If Content Loads Correctly

```sh
pipenv run scrapy view https://coldstorage.com.sg/beers-wines-spirits/beer-cidercraft-beers
```

Or you can inspect your browser and `Cmd + Shift + P` to `> Disable JavaScript` to check if the page loads using JavaScript
