from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import AccessTokenMalformedException, BaseApplicationException
from app.endpoints.api_router import api_router
from app.services.exceptions import (
    AccessViolationException,
    BaseServiceValidationException,
    NotFoundException,
    UniqueConstraintViolationException,
)

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
    # app.services exceptions
    NotFoundException: status.HTTP_404_NOT_FOUND,
    UniqueConstraintViolationException: status.HTTP_409_CONFLICT,
    BaseServiceValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AccessViolationException: status.HTTP_403_FORBIDDEN,
    # app.core exceptions
    AccessTokenMalformedException: status.HTTP_401_UNAUTHORIZED,
}


@application.exception_handler(BaseApplicationException)
async def application_exception_handler(
    request: Request, exception: BaseApplicationException
) -> Response:
    for exception_class in exceptions_to_http_status_codes:
        if isinstance(exception, exception_class):
            return await http_exception_handler(
                request,
                HTTPException(
                    status_code=exceptions_to_http_status_codes[exception_class],
                    detail=str(exception),
                ),
            )
    # if nothing matched - fall back to the generic HTTP 500 status code
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exception),
        ),
    )
