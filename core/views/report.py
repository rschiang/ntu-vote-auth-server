from core.models import Record
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .decorators import check_prerequisites, scheduled, login_required, permission
from .utils import error, exchange_token, logger
from account.models import User


@api_view(['POST'])
@scheduled
@login_required
@permission(User.STATION)
@check_prerequisites('uid', 'vote_token')
def report(request):
    token = exchange_token(request)
    if not token:
        return error('token_invalid')
    else:
        token.issued = True
        token.save()

    # Fetch record
    try:
        record = Record.objects.get(student_id=token.student_id)
    except Record.DoesNotExist:
        logger.exception('Record not found: %s', token.student_id)
        return error('token_invalid')

    if record.state != Record.LOCKED:
        logger.warning('Inconsistent state <%s> on %s, expect LOCKED', record.state, token.student_id)
        return error('token_invalid')

    record.state = Record.FLAGGED
    record.save()

    return Response({'status': 'success'})
