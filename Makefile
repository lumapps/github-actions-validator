SHELL:=/bin/bash

# Use python executables inside venv
export PATH := ./venv/bin:$(PATH)

.PHONY: tests

init: sync
	pre-commit install  # installs pre-commit hooks

sync: venv
	pip-sync dev-requirements.txt

venv:
	python3.12 -m venv venv
	pip install --quiet --upgrade pip
	pip install --quiet pip-tools

requirements.txt: venv requirements.in
	pip-compile \
		--quiet \
		--generate-hashes \
		--max-rounds=20 \
		--output-file requirements.txt \
		requirements.in

dev-requirements.txt: venv requirements.in dev-requirements.in
	pip-compile \
		--quiet \
		--generate-hashes \
		--max-rounds=20 \
		--output-file dev-requirements.txt \
		requirements.in dev-requirements.in

format:
	black src/ tests/
	isort src/ tests/

lint:
	pre-commit run -a

tests:
	pytest -xv tests
