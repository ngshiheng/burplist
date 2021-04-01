# Debugging and Development

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

## To see what scrapy sees

```sh
pipenv run scrapy view https://coldstorage.com.sg/beers-wines-spirits/beer-cidercraft-beers
```
