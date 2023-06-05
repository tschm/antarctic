#!/bin/bash
poetry run coverage run --source=antarctic/. -m pytest
poetry run coverage report -m
poetry run coverage html
open htmlcov/index.html
