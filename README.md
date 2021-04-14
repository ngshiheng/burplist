# Burplist

<br />

<div align="center"> <img src="https://media.giphy.com/media/3o85xjSETVG3OpPyx2/giphy.gif" width="200" height="200"/> </div>

> Collect all the available beers (preferably craft beers) data in Singapore into a single location so that users can easy compare prices across different vendors and shops.

## Start Crawling

### Run all spiders

```sh
scrapy list|xargs -n 1 scrapy crawl
```

### Run all spiders, in parallel

```sh
scrapy list|xargs -n 1 -P 0 scrapy crawl
```

### Without Proxy (For Development)

```sh
# Omit `-o filename.json` if you do not want to generate the output in json
pipenv run scrapy crawl alcoholdelivery -o alcoholdelivery.json
pipenv run scrapy crawl beerforce -o beerforce.json
pipenv run scrapy crawl brewerkz -o beerforce.json
pipenv run scrapy crawl coldstorage -o coldstorage.json
pipenv run scrapy crawl craftbeersg -o craftbeersg.json
pipenv run scrapy crawl fairprice -o fairprice.json
pipenv run scrapy crawl thirsty -o thristy.json --set=ROBOTSTXT_OBEY='False'
```

### Using Proxy (For Production)

```sh
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
pipenv run scrapy crawl coldstorage
```

## Database Schema

https://dbdiagram.io/d/605d3ad2ecb54e10c33d5165

## Useful Scrapy Tools and Libraries

https://github.com/croqaz/awesome-scrapy
