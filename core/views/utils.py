import logging
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger('vote')

def error(reason, status=status.HTTP_400_BAD_REQUEST):
    logger.info('Status code %s, reason %s', status, reason)
    return Response({'status': 'error', 'reason': reason}, status=status)
