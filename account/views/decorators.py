import logging
from core.utils import error
from django.utils.decorators import available_attrs
from functools import wraps
from rest_framework import status

logger = logging.getLogger('vote.auth')

def permission(*permission):
    def decorator(f):
        @wraps(f, assigned=available_attrs(f))
        def inner(request, *args, **kwargs):
            if request.user.kind not in permission:
                logger.error('Rejected %s to access %s: expect %s, got %s',
                             request.user, request.path, '/'.join(permission), request.user.kind)
                return error('permission_denied', status.HTTP_403_FORBIDDEN)
            return f(request, *args, **kwargs)
        return inner
    return decorator
