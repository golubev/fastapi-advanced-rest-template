# daily-rabbit-api


API backend for the brand new daily activities logging web application.

Frontend repo - https://github.com/golubev/daily-rabbit-frontend.


## Prerequisites (dependencies)

- Docker ^23.0
- Docker Compose plugin ^2.17


## Before you start

> ⚠️ Make sure you've created a `.env` file from the `.env.example` template:
> ```sh
> cp .env.example .env
> ```
> reviewed the values and changed were it was required.

## How to start with vscode

The vscode's Dev Containers, a remote development feature, are being used in order to get fully-integrated IDE with application's dockerized Python environment. And to get a decent developer experience (DX).

In order to run vscode inside the application's container do the following:

1. in vscode open the project's directory
2. hit Ctrl+Shift+P
3. paste `remote-containers.reopenInContainer`
4. hit Enter


## How to start without vscode

If the vscode is not an option for you, simply run:
```
docker compose up --detach --wait
```


## OpenAPI docs

Navigate to http://localhost:8000/docs
