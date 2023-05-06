#!/bin/bash

set -u
set -e

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py

black .
isort .
