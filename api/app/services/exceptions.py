class BaseServiceException(Exception):
    """
    Base class for any exception raised from a service.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class BaseServiceValidationException(BaseServiceException):
    """
    Base class for any validation exception raised from a service.
    """


class UniqueConstraintViolationException(BaseServiceValidationException):
    """
    Exception raised when a value violates a unique constraint violation.
    """


class AccessViolationException(BaseServiceException):
    """
    Base class for any access violation exception raised from a service.
    """


class OwnerAccessViolationException(AccessViolationException):
    """
    Exception raised when a user is forbidden to interact with an entity which he
    doesn't own.
    """
