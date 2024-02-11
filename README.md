# auto-post-classifier

## Dev Env Setup

Run `poetry install` from the root of the project.
This should get you all you need.

## Code Style and Conventions

- Make sure you use [Black](https://black.readthedocs.io/en/stable/) and
- sort the imports using [isort](https://pycqa.github.io/isort/)

Code that doesn't pass the tests in [`code_style_validation`] target of the `Makefile` won't be accepted.

## Run the app

first install the dependencies using poetry

```bash
# inside the root direcroy
poetry install
```

It is needed to create a `.env` file contains the necessary information for the app
to run. The field that needed to be defined can be found in the file: `example.env`

After that, run the app using

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 80 --reload
```

## install poetry

https://python-poetry.org/docs/

### debug with vscode

configure a launch.json for attching python process and run the program using

```
 python -m debugpy --listen 5678 auto_post_classifier/main.py --api -d data/AntiIsraeli.csv
```

### pytest

solve jupyter warining:

```
export JUPYTER_PLATFORM_DIRS=1
```

run only my-py test:

```
pytest --mypy -m mypy
```

### generate testing data set
1. get a `data-classified.csv` file
2. use `auto_post_classifier/testing_utils.py` to generate a sample.json file.
3. run the test using `pytest` from the root directory

