from fastapi import APIRouter

from app.endpoints import routes

api_router = APIRouter()

api_router.include_router(routes.login.router, tags=["Login"])
api_router.include_router(routes.users.router, tags=["Users"])


@api_router.get("/", tags=["Welcome"])
async def welcome_message() -> dict[str, str]:
    return {"message": "Hello world!"}
