from core.models import Record, AuthCode
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import check_prerequisites, error, exchange_token, logger

@api_view(['POST'])
def confirm(request):
    # Check if prerequisites match
    errors = check_prerequisites(request, 'uid', 'station', 'token')
    if errors:
        return errors

    token = exchange_token(request)
    if not token:
        return error('token_invalid')
    else:
        token.issued = True
        token.save()

    # Fetch record
    try:
        record = Record.object.get(student_id=token.student_id)
    except Record.DoesNotExist:
        logger.exception('Record not found: %s', token.student_id)
        return error('token_invalid')

    if record.state != Record.LOCKED:
        logger.warning('Inconsistent state <%s> on %s, expect LOCKED', record.state, token.student_id)
        return error('token_invalid')

    # Issue auth code
    code = AuthCode.objects.filter(kind=token.kind, issued=False).first()
    if code:
        record.state = Record.USED
        record.save()

        code.issued = True
        code.save()
    else:
        logger.info('Auth codes of kind %s have used up', token.kind)
        return error('out_of_auth_code', status=status.HTTP_503_SERVICE_UNAVAILABLE)

    logger.info('Auth code issued: %s', token.kind)
    return Response({'status': 'success', 'code': code.code})
