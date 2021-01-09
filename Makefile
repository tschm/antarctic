#!make
PROJECT_VERSION := $(shell python setup.py --version)

SHELL := /bin/bash
PACKAGE := antarctic

.PHONY: help build test doc tag 


.DEFAULT: help

help:
	@echo "make build"
	@echo "       Build the docker image."
	@echo "make test"
	@echo "       Build the docker image for testing and run them."
	@echo "make doc"
	@echo "       Construct the documentation."
	@echo "make tag"
	@echo "       Make a tag on Github."

build:
	docker-compose build antarctic

jupyter:
	echo "http://localhost:8888"
	docker-compose up jupyter

test:
	docker-compose -f docker-compose.test.yml run sut

doc:
	docker-compose -f docker-compose.test.yml run sut sphinx-build /source artifacts/build

tag: test
	git tag -a ${PROJECT_VERSION} -m "new tag"
	git push --tags

lint:
	docker-compose -f docker-compose.test.yml run lint