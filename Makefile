.PHONY: up \
	up-backend \
	npm-start \
	npm-install \
	help

.DEFAULT_GOAL := help

up: up-backend npm-start ## start both the frontend and the backend

up-backend: ## run docker compose up for the backend API
	docker compose up --detach --build --force-recreate --wait --remove-orphans

down-backend: ## run docker compose down for the backend API
	docker compose down

npm-start: ## run npm start for the frontend
	cd ./frontend; \
	npm start

npm-install: ## run npm install for the frontend
	cd ./frontend; \
	npm install

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
