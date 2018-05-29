import logging
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler

logger = logging.getLogger('vote')

def unwrap(data):
    if isinstance(data, list) and len(data) == 1:
        return data[0]
    return data

def rest_exception_handler(exc, context):
    # Let builtin exception handler process first
    # This will handle 404, 403, and general APIException
    response = exception_handler(exc, context)

    if response:
        reason = exc.__class__.__name__
        entity = {'status': 'error'}

        # Find the error code if available
        if isinstance(exc, APIException):
            reason = exc.get_codes()
            entity['code'] = unwrap(reason)

        # Wraps the response data if it is not in `dict`
        if not isinstance(response.data, dict):
            entity['detail'] = unwrap(response.data)
            response.data = entity

        # ValidationError returns `dict` but not in our favor
        elif isinstance(exc, ValidationError):
            entity['code'] = 'params_invalid'
            entity['detail'] = response.data
            response.data = entity
        else:
            response.data.update(entity)

        # Log our own error and set expectable status field
        logger.info('Status code %s, reason %s', response.status_code, reason)

    return response
