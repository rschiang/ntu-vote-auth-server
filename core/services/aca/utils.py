import struct
from . import meta
from ..errors import AuthenticationError, ExternalError

def reverse_indian(i):
    return struct.unpack('<I', struct.pack('>I', i))

def raise_exception(message):
    """
    Raises exception based on ACA error message traits.
    """
    # Try given error messages in meta
    for trait, code in meta.AUTHENTICATION_ERRORS:
        if trait in message:
            raise AuthenticationError(code=code)

    for trait, code in meta.SERVICE_ERRORS:
        if trait in message:
            raise ExternalError(code=code)

    # Either we were totally revoked access to ACA
    # or something was wrong with their server.
    raise ExternalError(detail=message)
