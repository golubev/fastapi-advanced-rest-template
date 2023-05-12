# API backend


## Database migrations

### Apply all migrations

```
alembic upgrade head
```

### Create a migration

Creates a new alembic revision (migration) according to diff in the models' source code and database schema:
```
alembic revision --autogenerate -m "create users table"
```


## Codestyle and code static analysis

### Linting the code

```
./do-lint.sh
```

### Autoformatting and cleaning the code

Autoformat the code, sort imports, remove unused imports, remove unused variables:
```
./do-autoformat-and-clean.sh
```


## Testing

### Running tests

```
./do-test.sh
```

### Running only specific tests

You may also filter tests to be run using the pytest `-k` flag.

E.g. by test function name:
```
./do-test.sh -k "test_create_user"
```

Or e.g. by test file:
```
./do-test.sh -k "user_service"
```


## Packages management

### Add a general dependency

```
poetry add fastapi@~0.95.1
```

### Add a dev dependency

```
poetry add --group dev httpx@~0.24.0
```

### Update dependencies and the `poetry.lock` file:

```
poetry update
```
