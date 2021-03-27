# Burplist

The goal here is to aggregate all the available beer (preferably craft beer) data in Singapore into a single location.

## Sources

-   https://beerforce.sg/
-   https://craftbeersg.com/
-   https://www.thirsty.com.sg/
-   https://www.alcoholdelivery.com.sg/

## Start crawling using a spider.

```sh
scrapy crawl craftbeersg
scrapy crawl coldstorage
```

## Database Schema

https://dbdiagram.io/d/605d3ad2ecb54e10c33d5165

## XPath Quick Guide

> “XPath is a language for addressing parts of an XML document”

-   https://dev.to/masihurmaruf/locator-strategy-xpath-54p7
-   https://docs.scrapy.org/en/xpath-tutorial/topics/xpath-tutorial.html
