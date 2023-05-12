# API backend


## Frequently used commands

### Add a Python dependency package

General dependency:
```
poetry add fastapi@~0.95.1
```

Dev dependency:
```
poetry add --group dev httpx@~0.24.0
```

Update dependencies and the `poetry.lock` file:
```
poetry update
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

Running tests:
```
./do-test.sh
```

You may also filter tests to be run using the pytest `-k` flag.

E.g. by test function name:
```
./do-test.sh -k "test_create_user"
```

Or e.g. by test file:
```
./do-test.sh -k "user_service"
```
