# daily-rabbit-api

A brand new daily activities logging web application.


## Prerequisites (dependencies)

- Docker ^23.0
- Docker Compose plugin ^2.17


## How to start with vscode

Dev Containers, the vscode's remote development feature, is being used in order to get fully-integrated IDE with application's dockerized Python environment. In order to run vscode inside the application's container do the following:

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
