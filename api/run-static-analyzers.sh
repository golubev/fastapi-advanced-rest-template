#!/bin/bash

set -u
set -e

echo "Running black"
echo

black . --check
echo "✅ black didn't find any issues"

echo
echo "Running isort"
echo

isort --check-only .
echo "✅ isort didn't find any issues"

echo
echo "Running flake8"
echo

flake8
echo "✅ flake8 didn't find any issues"

echo
echo "Running mypy"
echo

mypy .
echo "✅ mypy didn't find any issues"

echo
echo "🟢 all checks have passed successfully"
echo