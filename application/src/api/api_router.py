from fastapi import APIRouter

from src.api import routes

api_router = APIRouter()

api_router.include_router(routes.login.router, tags=["Login"])
api_router.include_router(routes.todo_items.router, tags=["TodoItems"])
api_router.include_router(routes.users.router, tags=["Users"])
