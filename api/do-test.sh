#!/bin/bash

set -u
set -e

if [ $ENVIRONMENT != "dev" ] && [ $ENVIRONMENT != "test" ]; then
    echo "Running tests allowed only in 'dev' or 'test' environments"
    exit 1
fi

POSTGRES_HOST_TEST="postgres_test"
POSTGRES_DB_TEST="test_database"
POSTGRES_USER_TEST="postgres"
POSTGRES_PASSWORD_TEST="test_password"

# override the database connection variables to the test ones
#
# NOTE: these overrides take effect in the current scripts' session only
export POSTGRES_HOST=$POSTGRES_HOST_TEST
export POSTGRES_DB=$POSTGRES_DB_TEST
export POSTGRES_USER=$POSTGRES_USER_TEST
export POSTGRES_PASSWORD=$POSTGRES_PASSWORD_TEST

# recreate the test database
PGPASSWORD=$POSTGRES_PASSWORD_TEST psql \
    -h $POSTGRES_HOST_TEST \
    -U $POSTGRES_USER_TEST \
    -c "DROP DATABASE IF EXISTS $POSTGRES_DB_TEST WITH (FORCE)"
PGPASSWORD=$POSTGRES_PASSWORD_TEST psql \
    -h $POSTGRES_HOST_TEST \
    -U $POSTGRES_USER_TEST \
    -c "CREATE DATABASE $POSTGRES_DB_TEST"

# apply all alembic migrations from the very beginning
alembic upgrade head

# insert test data into the database
python tests/seed_database.py

pytest --cov=app --cov-report=term-missing tests "${@}"
