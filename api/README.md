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
