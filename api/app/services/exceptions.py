from app.core.exceptions import BaseApplicationException


class BaseServiceException(BaseApplicationException):
    """
    Base class for any exception raised from a service.
    """


class NotFoundException(BaseServiceException):
    """
    Raised when a model is not found in the database.
    """


class BaseServiceValidationException(BaseServiceException):
    """
    Base class for any validation exception raised from a service.
    """


class UniqueConstraintViolationException(BaseServiceValidationException):
    """
    Raised when a value violates a unique constraint violation.
    """


class AccessViolationException(BaseServiceException):
    """
    Base class for any access violation exception raised from a service.
    """


class OwnerAccessViolationException(AccessViolationException):
    """
    Raised when a user is forbidden to interact with an entity which he
    doesn't own.
    """
