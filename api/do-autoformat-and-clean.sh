#!/bin/bash

set -u
set -e

# change the working dir to the application's root directory to make all
# tools' configs discoverable and all relative paths to be correct
SOURCE_CODE_DIR=$(dirname "$(readlink -f "$0")")
cd $SOURCE_CODE_DIR

# remove unused imports and variables
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py

# autoformat the code
black .

# sort imports
isort .
