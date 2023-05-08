#!/bin/bash

set -u
set -e

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_TO_AUTOFORMAT_DIR=$SCRIPT_DIR

# change the working dir to make all tools' configs discoverable
cd $SOURCE_TO_AUTOFORMAT_DIR

# remove unused imports and variables
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py

# autoformat the code
black .

# sort imports
isort .
