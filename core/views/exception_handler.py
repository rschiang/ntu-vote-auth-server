import logging
from rest_framework.views import exception_handler

logger = logging.getLogger('vote')


def rest_exception_handler(exc, context):
    # Let builtin exception handler process first
    # This will handle 404, 403, and general APIException
    response = exception_handler(exc, context)

    if response:
        # Log our own error
        reason = exc.detail or response.data or exc.__class__.__name__
        logger.info('Status code %s, reason %s', response.status_code, reason)
        response['status'] = 'error'

    return response
