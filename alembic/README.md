# Alembic

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
