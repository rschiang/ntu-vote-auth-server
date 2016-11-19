from .utils import error, event_available, logger
from account.models import Session, User
from django.conf import settings
from django.utils.decorators import available_attrs
from django.utils import timezone
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

def login_required(f):
    @wraps(f, assigned=available_attrs(f))
    def inner(request, *args, **kwargs):
        # Check parameters
        token = request.data.get('token', None)
        if token is None:
            logger.error('token required')
            return error('token_required', status.HTTP_401_UNAUTHORIZED)

        current_time = timezone.now()

        # Fetch session
        try:
            session = Session.objects.get(token=token)
        except Session.DoesNotExist:
            logger.error('API attempted failed for token %s', token)
            return error('unauthorized', status.HTTP_401_UNAUTHORIZED)

        session.last_seen = current_time
        session.save()

        if session.status is Session.EXPIRED:
            logger.info('Session (%s) expired', session.token[:10])
            return error('session_expired', status.HTTP_401_UNAUTHORIZED)
        request.user = session.user

        return f(request, *args, **kwargs)

    return inner


def permission(*permission):
    def decorator(f):
        @wraps(f, assigned=available_attrs(f))
        def inner(request, *args, **kwargs):
            logger.debug('Permission Required: %s', permission)
            logger.debug('user kind %s', request.user.kind)
            if request.user.kind not in permission:
                logger.error('Rejected %s to access %s', request.user, request.path)
                return error('permission_denied', status.HTTP_403_FORBIDDEN)

            if request.user.kind is User.STATION:
                if request.user.station.external_id:
                    request.station = str(request.user.station.external_id)
                else:
                    logger.error('Request from no id station (%s)', request.user.station.name)
                    return error('station_error')

            return f(request, *args, **kwargs)
        return inner
    return decorator
