from typing import Type

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler


class BaseApplicationException(Exception):
    """
    Base class for any exception raised from the application.
    """


class AccessTokenMalformedException(BaseApplicationException):
    """
    Raised when an access token is malformed.
    """


def add_application_exception_handler(
    application: FastAPI,
    exceptions_to_http_status_codes: dict[Type[BaseApplicationException], int],
) -> None:
    """
    Add an exception handler for all `BaseApplicationException` descendants by mapping
    them into response HTTP status codes.
    """

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
