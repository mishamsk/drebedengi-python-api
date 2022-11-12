.DEFAULT_GOAL := help

sources = drebedengi

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr site/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '.mypy_cache' -exec rm -fr {} +
	find . -name 'requirements-*.txt' -exec rm -fr {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr testtemp/

.PHONY: format
format:
	isort $(sources) tests
	black $(sources) tests

.PHONY: lint
lint:
	flake8 $(sources) tests
	mypy $(sources) tests

.PHONY: test
test: format lint unittest

.PHONY: unittest
unittest:
	pytest

.PHONY: coverage
coverage:
	pytest --cov=$(sources) --cov-branch --cov-report=term-missing tests

.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files

.PHONY: update-dev-deps
update-dev-deps:
	poetry add -G dev tox@latest
	poetry add -G dev tox-gh-actions@latest
	poetry add -G dev twine@latest
	poetry add -G dev black@latest
	poetry add -G dev flake8@latest
	poetry add -G dev isort@latest
	poetry add -G dev bump2version@latest
	poetry add -G dev pre-commit@latest
	poetry add -G test pytest@latest
	poetry add -G test pytest-cov@latest
	poetry add -G mypy mypy@latest

.PHONY: update-docs-deps
update-docs-deps:
	poetry add -G docs mkdocs@latest
	poetry add -G docs mkdocs-include-markdown-plugin@latest
	poetry add -G docs mkdocs-material-extensions@latest
	poetry add -G docs mkdocs-material@latest
	poetry add -G docs mkdocs-section-index@latest
	poetry add -G docs mkdocs-literate-nav@latest
	poetry add -G docs mkdocs-gen-files@latest
	poetry add -G docs mkdocs-exclude@latest
	poetry add -G docs mkdocs-autorefs@latest
	poetry add -G docs -e python mkdocstrings@latest
