#!make
IMAGE := lobnek/rstudio
SHELL := /bin/bash
VERSION := 3.1

include .env
export

.PHONY: help build jupyter hub


.DEFAULT: help

help:
	@echo "make build"
	@echo "       Build the docker image."
	@echo "make r"
	@echo "       Start the Jupyter server."
	@echo "make hub"
	@echo "       Push to Docker Hub"

build:
	docker-compose build r

r: build
	echo "http://localhost:${PORT}"
	docker-compose up r

hub:
	docker build -f Dockerfile --tag ${IMAGE}:latest --no-cache .
	docker push ${IMAGE}:latest
	docker tag ${IMAGE}:latest ${IMAGE}:${VERSION}
	docker push ${IMAGE}:${VERSION}
	docker rmi -f ${IMAGE}:${VERSION}
