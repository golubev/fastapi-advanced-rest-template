#!/bin/bash

set -u
set -e

if [ $ENVIRONMENT != "dev" ] && [ $ENVIRONMENT != "test" ]; then
    echo "Running tests is allowed only in 'dev' or 'test' environments."
    exit 1
fi

# change the working dir to the application's root directory to make all
# tools' configs discoverable and all relative paths to be correct
SOURCE_CODE_DIR=$(dirname "$(readlink -f "$0")")
cd $SOURCE_CODE_DIR

POSTGRES_HOST_TEST="postgres_test"
POSTGRES_DB_TEST="test_database"
POSTGRES_USER_TEST="postgres"
POSTGRES_PASSWORD_TEST="test_password"

if [ $ENVIRONMENT != "test" ]; then
    # override the database connection variables to the test ones to use
    # separate isolated databases for testing and deveoplment in `dev`
    # environments
    #
    # NOTE: these overrides take effect in the current scripts' session only
    export POSTGRES_HOST=$POSTGRES_HOST_TEST
    export POSTGRES_DB=$POSTGRES_DB_TEST
    export POSTGRES_USER=$POSTGRES_USER_TEST
    export POSTGRES_PASSWORD=$POSTGRES_PASSWORD_TEST
fi

# recreate the test database
PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h $POSTGRES_HOST \
    -U $POSTGRES_USER \
    -c "DROP DATABASE IF EXISTS $POSTGRES_DB WITH (FORCE)"
PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h $POSTGRES_HOST \
    -U $POSTGRES_USER \
    -c "CREATE DATABASE $POSTGRES_DB"

# apply all alembic migrations from the very beginning
alembic upgrade head

# insert test data into the database
python tests/seed_database.py

pytest --cov=app --cov-report=term-missing tests "${@}"
