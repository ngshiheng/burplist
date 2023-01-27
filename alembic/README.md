# Alembic

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

# SQLAlchemy

> https://github.com/dahlia/awesome-sqlalchemy

# Database Schema

> https://dbdiagram.io/d/605d3ad2ecb54e10c33d5165

## Example SQL Queries

1. To get the price list of all available products: [`psql postgres -h 127.0.0.1 -d burplist -f alembic/examples/product_price_list.sql`](./examples/product_price_list.sql)
2. To get the number of prices of all available products [`psql postgres -h 127.0.0.1 -d burplist -f alembic/examples/price_list.sql`](./examples/number_of_prices.sql)
