import logging
import re
from core.models import AuthToken
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
            logger.error('Invalid parameters')
            return error('params_invalid')

    # Assert API key and version match
    if request.DATA['api_key'] != settings.API_KEY:
        return error('unauthorized', status.HTTP_401_UNAUTHORIZED)
    elif request.DATA['version'] != '1':
        return error('version_not_supported')

    # All safe
    return None

def exchange_token(request):
    student_id = request.DATA['uid']
    station_id = request.DATA['station']
    token_code = request.DATA['token']

    # Check params
    if not (re.match(r'[A-Z]\d{2}[0-9A-Z]\d{5}', student_id) and re.match(r'\d+', station_id)):
        logger.info('Invalid parameter: user <%s>, station <%s>')
        return None

    # Fetch token from database
    try:
        token = AuthToken.objects.get(code=token_code, student_id=student_id, station_id=int(station_id))
    except AuthToken.DoesNotExist:
        logger.exception('Invalid auth token pair: (%s, %s, %s)', token_code, student_id, station_id)
        return None

    # Check state
    if token.issued:
        logger.info('Token already used')
        return None

    return token
