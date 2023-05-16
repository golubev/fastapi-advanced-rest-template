# fastapi-todo-rest


REST API backend for a TODO application. Inspired by [tiangolo/full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql) and [testdrivenio/fastapi-react](https://github.com/testdrivenio/fastapi-react).


## Prerequisites (dependencies)

- Docker ^23.0
- Docker Compose plugin ^2.17


## Before you start

> ⚠️ Make sure you've created a `.env` file from the `.env.example` template:
> ```sh
> cp .env.example .env
> ```
> and reviewed variables values in the `.env` file replacing `_CHANGE_THIS_` placeholders with appropriate values.


## How to start in vscode

The project was mainly configured to be developed in vscode. It is still available to be run simply with a CLI command without the vscode (see below).

The vscode's Dev Containers feature is used in order to reach a full integration of the IDE with the application's dockerized Python environment. That gives a decent developer experience (DX) working with the application's source code: code completion, code navigation etc.

In order to start the application and run vscode inside the application's container do the following:

1. in vscode open the project's directory
2. hit Ctrl+Shift+P
3. paste `remote-containers.reopenInContainer`
4. hit Enter


## How to start without vscode

If you simply want to spin up the application or if the vscode is not an option for you, just run:
```
docker compose up --detach --build --wait
```


## OpenAPI docs

Navigate to http://localhost:8000/docs
