# Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Setup

1. Install [poetry](https://python-poetry.org/docs/#installation).
2. Install all dependencies using `make dev`
3. Set up a local Postgres with Docker using `make setupdb`.

You may find other development guide [here](DEVELOPMENT.md).

> **Note**
> Check out the [Makefile](../Makefile) to find out what each command is doing.

## Steps

1. Fork this
2. Create your feature branch (`git checkout -b feature/bar`)
3. Please make sure you have installed the `pre-commit` hook and make sure it passes all the lint and format check
4. Commit your changes (`git commit -am 'feat: add some bar'`, make sure that your commits are [semantic](https://www.conventionalcommits.org/en/v1.0.0/#summary))
5. Push to the branch (`git push origin feature/bar`)
6. Create a new Pull Request
