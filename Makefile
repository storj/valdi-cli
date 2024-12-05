all: fmt lint

lint:
	find * -type f -name "*.py" -exec pylint --rcfile pylint.rc "{}" \;

fmt:
	find * -type f -name "*.py" -exec black "{}" \;

deps:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

.PHONY: fmt lint deps all
