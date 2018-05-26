# Errors used in external services
from rest_framework.exceptions import APIException

class ExternalError(APIException):
    """
    External API service error.
    """
    status_code = 503
    default_code = 'external_error'
    default_detail = 'Error occured in external service.'

class AuthenticationError(APIException):
    """
    Raises when ACA authentication failed.
    """
    status_code = 401
    default_code = 'auth_error'
    default_detail = 'Authentication failed with ACA.'

class NotImplemented(Exception):
    """
    The API function has not yet been implemented.
    """
    pass
