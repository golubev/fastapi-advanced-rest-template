from fastapi import APIRouter

from app.endpoints import routes

api_router = APIRouter()

api_router.include_router(routes.login.router, tags=["Login"])
api_router.include_router(routes.tasks.router, tags=["Tasks"])
api_router.include_router(routes.users.router, tags=["Users"])
