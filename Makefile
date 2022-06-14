install:
	poetry install --no-root

test:
	poetry run python3 -m unittest

lint:
	poetry run flake8 --statistics --show-source

pre-commit:
	poetry run pre-commit run
