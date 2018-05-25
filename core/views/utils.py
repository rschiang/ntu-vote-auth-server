import logging
import re
from core.models import AuthToken
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger('vote')


def error(reason, status=status.HTTP_400_BAD_REQUEST):
    logger.info('Status code %s, reason %s', status, reason)
    return Response({'status': 'error', 'reason': reason}, status=status)


def exchange_token(request):
    student_id = request.data['uid']
    station_id = str(request.station)
    token_code = request.data['vote_token']

    # Check params
    if not (re.match(r'[A-Z]\d{2}[0-9A-Z]\d{5}', student_id) and re.match(r'\d+', station_id)):
        logger.info('Invalid parameter: user <%s>, station <%s>', student_id, station_id)
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
