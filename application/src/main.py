from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.api_router import api_router
from src.api.errors import exceptions_to_http_status_codes
from src.core.exceptions import add_application_exception_handler

application = FastAPI()
application.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
application.include_router(api_router)

add_application_exception_handler(application, exceptions_to_http_status_codes)


@application.get("/ping", tags=["Healthcheck"])
def ping() -> dict[str, str]:
    return {"message": "pong"}
