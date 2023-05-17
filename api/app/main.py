from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core import exceptions as core_exceptions
from app.core.exceptions import add_application_exception_handler
from app.endpoints.api_router import api_router
from app.services import exceptions as services_exceptions

application = FastAPI()
application.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
application.include_router(api_router)


@application.get("/ping", tags=["Healthcheck"])
def ping() -> dict[str, str]:
    return {"message": "pong"}


# application's exceptions mapped into HTTP status codes
#
# While being handled exceptions are being checked against the map in the order of the
# map. The most basic exceptions SHOULD be put in the end of this dictionary
#
# Any application's custom exception SHOULD be derived from the
# `app.core.exceptions.BaseApplicationException`.
#
# If an exception is not present in the dictionary below it will be handled like a
# generic exception falling back to HTTP 500 status code.
exceptions_to_http_status_codes = {
    services_exceptions.NotFoundException: status.HTTP_404_NOT_FOUND,
    services_exceptions.UniqueConstraintViolationException: status.HTTP_409_CONFLICT,
    services_exceptions.ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    services_exceptions.AccessViolationException: status.HTTP_403_FORBIDDEN,
    services_exceptions.StateConflictException: status.HTTP_409_CONFLICT,
    core_exceptions.AccessTokenMalformedException: status.HTTP_401_UNAUTHORIZED,
}

add_application_exception_handler(application, exceptions_to_http_status_codes)
