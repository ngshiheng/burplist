# Burplist

The goal here is to aggregate all the available beer (preferably craft beer) data in Singapore into a single location.

## Sources

-   https://beerforce.sg/
-   https://craftbeersg.com/
-   https://www.thirsty.com.sg/
-   https://www.alcoholdelivery.com.sg/

## Start Crawling

```sh
pipenv run scrapy crawl craftbeersg
pipenv run scrapy crawl coldstorage
pipenv run scrapy crawl fairprice
```

## Database Schema

https://dbdiagram.io/d/605d3ad2ecb54e10c33d5165

## XPath Quick Guide

> “XPath is a language for addressing parts of an XML document”

-   https://dev.to/masihurmaruf/locator-strategy-xpath-54p7
-   https://docs.scrapy.org/en/xpath-tutorial/topics/xpath-tutorial.html

# Selecting Dynamically-loaded Content

-   https://docs.scrapy.org/en/latest/topics/dynamic-content.html
-   https://www.zyte.com/blog/handling-javascript-in-scrapy-with-splash/

```sh
docker run -d -p 8050:8050 scrapinghub/splash
```

## Using `scrapy-splash` with `scrapy` shell

```sh
# Example
pipenv run scrapy shell 'http://localhost:8050/render.html?url=https://www.alcoholdelivery.com.sg/beer-cider/craft-beer'
```

## To see what scrapy sees

```sh
scrapy view https://coldstorage.com.sg/beers-wines-spirits/beer-cidercraft-beers
```
