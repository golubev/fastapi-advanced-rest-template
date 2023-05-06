from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints import routes

application = FastAPI()


application.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application.include_router(routes.login.router, tags=["Login"])
application.include_router(routes.users.router, tags=["Users"])


@application.get("/", tags=["Welcome"])
async def welcome_message() -> dict[str, str]:
    return {"message": "Hello world!"}
