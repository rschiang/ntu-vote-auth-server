from core.models import Record, AuthToken
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .decorators import scheduled
from .utils import error, logger


@api_view(['GET'])
@scheduled
def complete(request):
    try:
        confirm_code = request.GET.get('callback')
        token = AuthToken.objects.get(confirm_code=confirm_code)

    except KeyError:
        logger.exception('Fail to get the callback argument')
        return error('confirm_code_invalid', status=status.HTTP_400_BAD_REQUEST)

    except AuthToken.DoesNotExist:
        logger.exception('Invalid confirm code, %s', confirm_code)
        return error('confirm_code_invalid')

    else:
        logger.info('Receive a callback argument %s', confirm_code)

    # Fetch Record
    try:
        record = Record.objects.get(student_id=token.student_id)
    except Record.DoesNotExist:
        logger.exception('Record not found: %s', token.student_id)
        return error('token_invalid')

    if record.state == Record.USED:
        logger.warning('Inconsistent state <%s> on %s, expect VOTING', record.state, token.student_id)
        return Response({'status': 'success', 'message': 'duplicated callback'},
                        status=status.HTTP_304_NOT_MODIFIED)

    if record.state != Record.VOTING:
        logger.warning('Inconsistent state <%s> on %s, expect VOTING', record.state, token.student_id)
        return error('token_invalid', status=status.HTTP_403_FORBIDDEN)

    # Complete the voting process
    record.state = Record.USED
    record.save()
    logger.info('%s completes voting process', token.student_id)
    return Response({'status': 'success', 'message': 'all correct'}, status=status.HTTP_200_OK)
