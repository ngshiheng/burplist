## Alembic

We use [alembic](https://alembic.sqlalchemy.org/en/latest/) to manage our database migrations for Burplist.

Alembic is a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.

## Steps to generate migration

1. `alembic --autogenerate -m "A concise commit message."`
2. Check the auto-generated migration file to see if it makes any sense
3. Once confirm, run `alembic upgrade head` to apply the database migration (Otherwise simply just delete the generated migration file)
4. You can always use `alembic downgrade -1` to revert any database migrations

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
SELECT
	product_id,
	platform AS "Platform",
	name AS "Product Name",
	brand AS "Brand",
	style AS "Style",
	abv AS "ABV",
	volume AS "Volume (mL)",
	round(price::numeric, 2) AS "Price ($SGD)",
	quantity AS "Quantity (Unit)",
	round((price / quantity)::numeric, 2) AS "Price/Quantity ($SGD)",
	url AS "Product Link",
	TO_CHAR(price.updated_on::TIMESTAMP AT TIME ZONE 'SGT', 'dd/mm/yyyy') AS "Updated On (SGT)"
FROM
	product
	INNER JOIN price ON price.product_id = product.id
ORDER BY
	price / quantity ASC
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
