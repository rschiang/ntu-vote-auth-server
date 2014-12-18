import re
from core.models import Record, AuthCode, AuthToken
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import check_prerequisites, logger, error

@api_view(['POST'])
def confirm(request):
    # Check if prerequisites match
    errors = check_prerequisites(request, 'uid', 'station', 'token')
    if errors:
        return errors

    student_id = request.DATA['uid']
    station_id = request.DATA['station']
    token_code = request.DATA['token']

    if not (re.match(r'[A-Z]\d{2}[0-9A-Z]\d{5}', student_id) and re.match(r'\d+', station_id)):
        logger.info('Invalid parameter: user <%s>, station <%s>')
        return error('params_invalid')

    # Fetch token from database
    try:
        token = AuthToken.objects.get(code=token_code, student_id=student_id, station_id=int(station_id))
        if token.issued:
            logger.info('Token already used')
            return error('token_invalid')

    except AuthToken.DoesNotExist:
        logger.exception('Invalid auth token pair: (%s, %s, %s)', token_code, student_id, station_id)
        return error('token_invalid')

    # Fetch record
    try:
        record = Record.object.get(student_id=student_id)
        if record.state != Record.LOCKED:
            logger.warning('Inconsistent state: %s with state [%s]', student_id, record.state)
            return error('token_invalid')

    except Record.DoesNotExist:
        logger.exception('Record not found: %s', student_id)
        return error('token_invalid')

    # Issue auth code
    code = AuthCode.objects.filter(kind=token.kind, issued=False).first()
    if code:
        token.issued = True
        token.save()

        record.state = Record.USED
        record.save()

        code.issued = True
        code.save()
    else:
        logger.info('Auth codes of kind %s have used up', token.kind)
        return error('out_of_auth_code', status=status.HTTP_503_SERVICE_UNAVAILABLE)

    logger.info('Auth code issued: %s', token.kind)
    return Response({'status': 'success', 'code': code.code})
