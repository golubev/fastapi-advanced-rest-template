from typing import Type

from fastapi import status

from src.core import exceptions as core_exceptions
from src.services import exceptions as services_exceptions

"""
Application's exceptions mapped into HTTP status codes

While being handled exceptions are being checked against the map in the order of the \
map. The most basic exceptions SHOULD be put in the end of this dictionary.

Any application's custom exception SHOULD be derived from the
`src.core.exceptions.BaseApplicationException`.

If an exception is not present in the dictionary below it will be handled like a
generic exception falling back to HTTP 500 status code.
"""
exceptions_to_http_status_codes: dict[
    Type[core_exceptions.BaseApplicationException], int
] = {
    services_exceptions.NotFoundException: status.HTTP_404_NOT_FOUND,
    services_exceptions.UniqueConstraintViolationException: status.HTTP_409_CONFLICT,
    services_exceptions.ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    services_exceptions.AccessViolationException: status.HTTP_403_FORBIDDEN,
    services_exceptions.StateConflictException: status.HTTP_409_CONFLICT,
    core_exceptions.AccessTokenMalformedException: status.HTTP_401_UNAUTHORIZED,
}
