from core.models import Record, AuthCode
from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework import status
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
def confirm(request):
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

    # Issue auth code
    code = AuthCode.objects.filter(kind=token.kind, issued=False).first()
    if code:
        record.state = Record.VOTING
        record.save()

        code.issued = True
        code.save()
    else:
        logger.info('Auth codes of kind %s have used up', token.kind)
        return error('out_of_auth_code', status=status.HTTP_503_SERVICE_UNAVAILABLE)

    logger.info('Auth code issued: %s', token.kind)
    callback = {
        'uri': request.build_absolute_uri(reverse('elector:callback')),
        'code': token.confirm_code,
    }
    return Response({
        'status': 'success', 'ballot': code.code,
        'callback': '{uri}?callback={code}'.format(**callback)
    })
