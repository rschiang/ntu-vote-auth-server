# Errors used in external services

class ExternalError(Exception):
    """
    External API service error.
    """
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)

class NotImplemented(Exception):
    """
    The API function has not yet been implemented.
    """
    pass
