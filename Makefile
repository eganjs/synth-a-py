.PHONY: all
all: lint test

.PHONY: lint
lint: .venv
	poetry run mypy synth_a_py tests
	poetry run flake8 synth_a_py tests
	poetry run isort --check-only --profile black synth_a_py tests
	poetry run black --check --diff synth_a_py tests

.PHONY: fmt
fmt: .venv
	poetry run isort --profile black synth_a_py tests
	poetry run black synth_a_py tests

.PHONY: test
test: .venv
	poetry run pytest --verbose --capture=no

.PHONY: publish
publish: dist
	poetry publish

.PHONY: dist
dist: dist/synth-a-py-1.3.1.tar.gz dist/synth_a_py-1.3.1-py3-none-any.whl

dist/synth-a-py-1.3.1.tar.gz dist/synth_a_py-1.3.1-py3-none-any.whl: $(shell find synth_a_py -type f -name '*.py')
	poetry build

.venv: poetry.lock
	poetry install
	@touch -c .venv

poetry.lock: pyproject.toml
	poetry lock
	@touch -c poetry.lock
