## Alembic

We use [alembic](https://alembic.sqlalchemy.org/en/latest/) to manage our database migrations for Burplist.

Alembic is a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.

## Steps to generate migration

1. `alembic revision --autogenerate -m "A concise commit message."`
2. Check the auto-generated migration file to see if it makes any sense
3. Once confirm, run `alembic upgrade head` to apply the database migration (Otherwise simply just delete the generated migration file)

_NOTE: You can always use `alembic downgrade -1` to revert any database migrations_

## How to generate migration for an existing database

-   https://stackoverflow.com/a/56651578/10067850
-   Remember to run `alembic stamp head` to tell `sqlalchemy` that the current migration represents the state of the database

---

## SQLAlchemy

### List of awesome SQLAlchemy libraries

-   https://github.com/dahlia/awesome-sqlalchemy

---

## Database Schema

-   https://dbdiagram.io/d/605d3ad2ecb54e10c33d5165

### List of awesome Scrapy libraries

-   https://github.com/croqaz/awesome-scrapy

### Useful SQL Queries

To get the price list of all available products:

```sql
WITH CURRENT_PRICE (product_id, price) AS (
    SELECT
        product_id,
        price
    FROM
        (
            SELECT
                product_id,
                price,
                ROW_NUMBER() OVER (
                    PARTITION BY product_id
                    ORDER BY
                        price.updated_on DESC
                ) AS rownum
            FROM
                price
        ) t
    WHERE
        rownum = 1
),
PREVIOUS_PRICE (product_id, price) AS (
    SELECT
        product_id,
        price,
        updated_on
    FROM
        (
            SELECT
                product_id,
                price,
                updated_on,
                ROW_NUMBER() OVER (
                    PARTITION BY product_id
                    ORDER BY
                        price.updated_on DESC
                ) AS rownum
            FROM
                price
        ) t
    WHERE
        rownum = 2
)
SELECT
    platform AS "Platform",
    name AS "Product Name",
    brand AS "Brand",
    style AS "Style",
    abv AS "ABV (%)",
    volume AS "Volume (mL)",
    curr.price AS "Current ($SGD)",
    prev.price AS "Previous ($SGD)",
    CASE
        WHEN prev.price IS NULL THEN NULL
        ELSE round((curr.price - prev.price) :: numeric, 2)
    END AS "Change ($SGD)",
    quantity AS "Quantity",
    round((curr.price / quantity) :: numeric, 2) AS "Price/Quantity ($SGD)",
    url AS "Product URL",
    TO_CHAR(
        p.updated_on + INTERVAL '8 HOUR',
        'DD-MON-YYYY HH24:MM'
    ) AS "Last Checked",
    TO_CHAR(
        prev.updated_on + INTERVAL '8 HOUR',
        'DD-MON-YYYY HH24:MM'
    ) AS "Last Change"
FROM
    product p
    LEFT JOIN CURRENT_PRICE curr ON curr.product_id = p.id
    LEFT JOIN PREVIOUS_PRICE prev ON prev.product_id = p.id
    AND(prev.price <> curr.price)
```

To get the number of prices of all available products:

```sql
SELECT
	product.id,
	platform AS "Platform",
	brand AS "Brand",
	name AS "Product Name",
	quantity AS "Quantity (Unit)",
	url AS "Product Link",
	count(price.product_id) AS "Number of Prices"
FROM
	product
	LEFT JOIN price ON (product.id = price.product_id)
GROUP BY
	product.id
```
