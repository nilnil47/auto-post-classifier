# auto-post-classifier

## Dev Env Setup

Run `poetry install` from the root of the project.
This should get you all you need.

## Code Style and Conventions

- Make sure you use [Black](https://black.readthedocs.io/en/stable/) and
- sort the imports using [isort](https://pycqa.github.io/isort/)

Code that doesn't pass the tests in [`code_style_validation`] target of the `Makefile` won't be accepted.

## Run the script

The script should be installed as an executable in the environment created by `poetry` (see above).
It is possible to run the script in one of two ways:

### Directly

```
poetry run python auto_post_classifier/main.py
```

Use this method during dev.

### install as systemd service

```
sudo cp auto-post-classifier.service /etc/systemd/system/auto-post-classifier.service
```

### Indirectly

First start the environment with `poetry shell` executed from the project's root directory and then simply execute `auto-post-classifier`

## install poetry

https://python-poetry.org/docs/
