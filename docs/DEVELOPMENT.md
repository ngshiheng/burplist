# Development, Debug & Troubleshoot

- [Development, Debug \& Troubleshoot](#development-debug--troubleshoot)
  - [Poetry Setup](#poetry-setup)
  - [Database Setup](#database-setup)
  - [XPath Quick Guide](#xpath-quick-guide)
  - [Scrapy Shell](#scrapy-shell)
  - [How-to's](#how-tos)
    - [Add delay to requests](#add-delay-to-requests)
    - [Work with Scrapy contracts](#work-with-scrapy-contracts)
    - [Use item loaders](#use-item-loaders)
    - [Unit test Scrapy spiders](#unit-test-scrapy-spiders)
    - [Bulk insert in SQLAlchemy](#bulk-insert-in-sqlalchemy)
    - [Deal with JavaScript heavy websites](#deal-with-javascript-heavy-websites)
  - [References](#references)
    - [List of awesome Scrapy libraries](#list-of-awesome-scrapy-libraries)
    - [Docker](#docker)

## Poetry Setup

_TL;DR run `make dev`_

## Database Setup

_TL;DR run `make setupdb`_

```sh
# To spin up a PostgreSQL Docker container
docker run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest

# To run `psql` in the Docker container
docker exec -it dpostgres psql -U postgres
```

## XPath Quick Guide

> “XPath is a language for addressing parts of an XML document”

It is highly recommended to read these materials about XPath, it will save you a lot of time:

-   https://dev.to/masihurmaruf/locator-strategy-xpath-54p7
-   https://docs.scrapy.org/en/xpath-tutorial/topics/xpath-tutorial.html

## Scrapy Shell

```sh
# Run splash in Docker
docker run -d -p 8050:8050 scrapinghub/splash

# Run scrapy shell on a specific webpage
poetry run scrapy shell 'http://localhost:8050/render.html?url=https://www.alcoholdelivery.com.sg/beer-cider/craft-beer'
```

```python
## Deleting a product

import logging

from sqlalchemy.exc import ProgrammingError

from burplist.database.models import Price, Product
from burplist.database.utils import Session

logger = logging.getLogger(__name__)

def remove_products_prices(name: str) -> None:
    """Remove products and their prices based on name matching using ILIKE"""
    with Session() as session:
        products = session.query(Product).filter(Product.name.ilike(f'%{name}%'))
        products_count = products.count()
        logger.info(f"Found {products_count} stale products.")

        if products_count < 1:
            logger.info("No products to delete.")
            return

        product_ids = [product.id for product in products.all()]
        prices = session.query(Price).filter(Price.product_id.in_(product_ids))
        logger.info(f"Found {prices.count()} prices.")

        prices.delete(synchronize_session=False)
        products.delete(synchronize_session=False)
        session.commit()

        logger.info(f"{products_count} products deleted successfully.")
```

## How-to's

### Add delay to requests

-   https://stackoverflow.com/questions/19135875/add-a-delay-to-a-specific-scrapy-request/64903556#64903556
-   https://stackoverflow.com/questions/41404281/how-to-retry-the-request-n-times-when-an-item-gets-an-empty-field/41404391#41404391

### Work with Scrapy contracts

-   https://stackoverflow.com/questions/25764201/how-to-work-with-the-scrapy-contracts

### Use item loaders

-   https://towardsdatascience.com/demystifying-scrapy-item-loaders-ffbc119d592a

### Unit test Scrapy spiders

-   https://stackoverflow.com/questions/6456304/scrapy-unit-testing

### Bulk insert in SQLAlchemy

-   [I’m inserting 400,000 rows with the ORM and it’s really slow!](https://docs.sqlalchemy.org/en/13/faq/performance.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow)
-   https://stackoverflow.com/questions/36386359/sqlalchemy-bulk-insert-with-one-to-one-relation

### Deal with JavaScript heavy websites

You can inspect your browser and `Cmd + Shift + P` to `> Disable JavaScript` to check if the page loads using JavaScript.

```sh
poetry run scrapy view https://coldstorage.com.sg/beers-wines-spirits/beer-cidercraft-beers
```

-   https://thepythonscrapyplaybook.com/
-   https://docs.scrapy.org/en/latest/topics/dynamic-content.html
-   https://www.zyte.com/blog/handling-javascript-in-scrapy-with-splash/

## References

### List of awesome Scrapy libraries

-   https://github.com/croqaz/awesome-scrapy
-   https://github.com/groupbwt/scrapy-boilerplate

### Docker

-   https://stackoverflow.com/questions/60340228/how-to-connect-to-postgres-created-with-docker-compose-from-outside-host
-   https://stackoverflow.com/questions/50983177/how-to-connect-to-postgresql-using-docker-compose/52543774
-   https://stackoverflow.com/questions/30063907/using-docker-compose-how-to-execute-multiple-commands
