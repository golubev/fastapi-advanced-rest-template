#!/bin/bash

set -u
set -e

# change the working dir to the application's root directory to make all
# tools' configs discoverable and all relative paths to be correct
SOURCE_CODE_DIR=$(dirname "$(readlink -f "$0")")
cd $SOURCE_CODE_DIR

echo
echo "# linting the Python code"

echo
echo "# running black"
echo

black . --check
echo "✔️ black didn't find any issues"

echo
echo "# running isort"
echo

isort --check-only .
echo "✔️ isort didn't find any issues"

echo
echo "# running flake8"
echo

flake8 .
echo "✔️ flake8 didn't find any issues"

echo
echo "# running mypy"
echo

mypy .
echo "✔️ mypy didn't find any issues"

echo
echo "🟢 all checks have passed successfully"
echo
