import logging
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger('vote')

def error(reason, status=status.HTTP_400_BAD_REQUEST):
    logger.info('Status code %s, reason %s', status, reason)
    return Response({'status': 'error', 'reason': reason}, status=status)

def event_available():
    if settings.ENFORCE_EVENT_DATE:
        tz = timezone.get_default_timezone()
        start_date = timezone.make_aware(settings.EVENT_START_DATE, tz)
        end_date = timezone.make_aware(settings.EVENT_END_DATE, tz)

        if not (start_date <= timezone.now() <= end_date):
            return False
    return True

def check_prerequisites(request, *params):
    # Check event timespan
    if not event_available():
        return error('service_closed')

    # Check parameters
    for key in (('api_key', 'version') + params):
        if key not in request.DATA:
            logger.exception('Invalid parameters')
            return error('params_invalid')

    # Assert API key and version match
    if request.DATA['api_key'] != settings.API_KEY:
        return error('unauthorized', status.HTTP_401_UNAUTHORIZED)
    elif request.DATA['version'] != '1':
        return error('version_not_supported')

    # All safe
    return None
