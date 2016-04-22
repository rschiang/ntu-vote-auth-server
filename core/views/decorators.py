from .utils import error, event_available, logger
from django.conf import settings
from django.utils.decorators import available_attrs
from functools import wraps
from rest_framework import status

def scheduled(f):
    @wraps(f, assigned=available_attrs(f))
    def inner(request, *args, **kwargs):
        # Check event timespan
        if not event_available():
            return error('service_closed')
        return f(request, *args, **kwargs)
    return inner

def check_prerequisites(*params):
    def decorator(f):
        @wraps(f, assigned=available_attrs(f))
        def inner(request, *args, **kwargs):
            # Check parameters
            for key in (('api_key', 'version') + params):
                if key not in request.data:
                    logger.error('Invalid parameters')
                    return error('params_invalid')

            # Assert API key and version match
            if request.data['api_key'] != settings.API_KEY:
                return error('unauthorized', status.HTTP_401_UNAUTHORIZED)
            elif request.data['version'] != settings.API_VERSION:
                return error('version_not_supported')

            # All safe
            response = f(request, *args, **kwargs)
            return response

        return inner
    return decorator
