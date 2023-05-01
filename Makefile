.PHONY: up \
	up-backend \
	down-backend \
	pip-install \
	npm-run-dev \
	npm-install \
	help

.DEFAULT_GOAL := help

up: up-backend npm-run-dev ## start both the frontend and the backend

up-backend: ## run docker compose up for the backend API
	docker compose up --detach --build --force-recreate --wait --remove-orphans

down-backend: ## run docker compose down for the backend API
	docker compose down

pip-install: ## run pip install for the backend
	docker compose run --rm backend-api python3 -m pip install --requirement ./requirements.txt --target ./.vendor-packages

npm-run-dev: ## run npm start for the frontend
	cd ./frontend; \
	npm run dev

npm-install: ## run npm install for the frontend
	cd ./frontend; \
	npm install

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
