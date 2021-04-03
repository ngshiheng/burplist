# Burplist

The goal here is to aggregate all the available beer (preferably craft beer) data in Singapore into a single location

## Start Crawling

### Without Proxy (For Development)

```sh
pipenv run scrapy crawl craftbeersg -o craftbeersg.json
pipenv run scrapy crawl coldstorage -o coldstorage.json
pipenv run scrapy crawl fairprice -o fairprice.json
pipenv run scrapy crawl beerforce -o beerforce.json
pipenv run scrapy crawl alcoholdelivery -o alcoholdelivery.json
pipenv run scrapy crawl thirsty -o thristy.json --set=ROBOTSTXT_OBEY='False'
```

### Using Proxy (For Production)

```sh
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
pipenv run scrapy crawl craftbeersg -o craftbeersg.json --set=ROBOTSTXT_OBEY='False'
```

## Database Schema

https://dbdiagram.io/d/605d3ad2ecb54e10c33d5165
