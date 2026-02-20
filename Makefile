.PHONY: install lint type test check format lint-type-test docs

install:
	poetry install --with dev,ci

lint:
	poetry run ruff check speechmarkdown
	poetry run black --check speechmarkdown tests
	poetry run isort --check-only speechmarkdown tests

type:
	poetry run mypy -p speechmarkdown

test:
	poetry run pytest

format:
	poetry run isort speechmarkdown tests
	poetry run ruff check --fix --unsafe-fixes speechmarkdown
	poetry run black speechmarkdown tests

# Combined lint, type check, and test command
lint-type-test:
	poetry run ruff check speechmarkdown
	poetry run isort --check-only speechmarkdown tests
	poetry run black --check speechmarkdown tests
	poetry run mypy -p speechmarkdown
	poetry run pytest

check:
	# Run comprehensive checks across all Python versions
	@for version in 3.11 3.12 3.13; do \
		echo "Checking with Python $$version..."; \
		mise exec python@$$version -- make lint-type-test; \
	done

docs:
	poetry run make -C docs html

docs-serve:
	poetry run sphinx-autobuild docs docs/_build/html
