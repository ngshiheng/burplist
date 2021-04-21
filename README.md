<h1 align="center"><strong>Burplist</strong></h1>

<p align="center">
  <img width="300" height="300" src="https://media.giphy.com/media/3o85xjSETVG3OpPyx2/giphy.gif">
</p>
<br />

> Collect all the available beers (preferably craft beers 🍻) data in Singapore into a single place so that users can easy compare prices across different vendors and shops.

## Start Crawling

### Run single spider

```sh
# To list all spiders
pipenv run scrapy crawl list

# To run a single spider
pipenv run scrapy crawl fairprice -o fairprice.json

# To run single spider with json output
pipenv run scrapy crawl coldstorage -o coldstorage.json
```

### Run all spiders

```sh
pipenv run scrapy list | xargs -n 1 pipenv run scrapy crawl

# Run on Heroku
heroku run scrapy list | xargs -n 1 heroku run scrapy crawl
```

### Run all spiders, in parallel

```sh
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

## Using Proxy (For Production)

```sh
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
```

## Database Schema

https://dbdiagram.io/d/605d3ad2ecb54e10c33d5165

## Useful Scrapy Tools and Libraries

https://github.com/croqaz/awesome-scrapy
