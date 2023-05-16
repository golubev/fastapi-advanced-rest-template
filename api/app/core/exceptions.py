class BaseApplicationException(Exception):
    """
    Base class for any exception raised from the application.
    """


class AccessTokenMalformedException(BaseApplicationException):
    """
    Raised when an access token is malformed.
    """
