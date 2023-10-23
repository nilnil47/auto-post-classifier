.PHONY: code_style_validation
code_style_validation:
	poetry run isort --check .
	poetry run black --check --diff .
	poetry run flake8 .
