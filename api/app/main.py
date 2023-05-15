from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.api_router import api_router
from app.services.exceptions import (
    AccessViolationException,
    BaseServiceException,
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


service_exceptions_to_status_codes = {
    NotFoundException: status.HTTP_404_NOT_FOUND,
    UniqueConstraintViolationException: status.HTTP_409_CONFLICT,
    BaseServiceValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AccessViolationException: status.HTTP_403_FORBIDDEN,
}


@application.exception_handler(BaseServiceException)
async def service_exception_handler(
    request: Request, exception: BaseServiceException
) -> Response:
    for exception_class in service_exceptions_to_status_codes:
        if isinstance(exception, exception_class):
            return await http_exception_handler(
                request,
                HTTPException(
                    status_code=service_exceptions_to_status_codes[exception_class],
                    detail=exception.message,
                ),
            )
    # if nothing matched - return a generic 500 HTTP server error code
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exception.message,
        ),
    )
