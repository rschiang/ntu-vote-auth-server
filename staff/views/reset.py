from core.models import Record
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import login_required, permission, check_prerequisites
from account.models import User
from core.views.utils import logger, error


@api_view(['GET'])
@login_required
@permission(User.ADMIN, User.SUPERVISOR)
def reset_list(request):
    return Response({
        'status': 'success',
        'target': [{'student_id': r.student_id} for r in Record.objects.filter(state=Record.RESETTING)],
    })


@api_view(['POST'])
@login_required
@permission(User.ADMIN)
@check_prerequisites('uid')
def apply_reset(request):
    uid = request.data['uid']

    # Fetch Elector
    try:
        record = Record.objects.get(student_id=uid)

    except Record.DoesNotExist:
        logger.error('reset target (%s) not found', uid)
        return error('student_not_found')

    # Log this event
    logger.info('Admin %s create a reset request (%s - %s)', request.user.username, uid, record.state)

    record.state = Record.RESETTING
    record.save()

    return Response({
        'status': 'success',
        'message': 'reset request created',
    })


@api_view(['POST'])
@login_required
@permission(User.SUPERVISOR)
@check_prerequisites('uid')
def confirm_reset(request):
    uid = request.data['uid']

    # Fetch Elector
    try:
        record = Record.objects.get(student_id=uid)

    except Record.DoesNotExist:
        logger.error('student (%s) not found', uid)
        return error('student_not_found')

    # Checking elector state
    if record.state != Record.RESETTING:
        logger.info('reset request (%s) not found', uid)
        return error('reset_request_not_found')

    # Log this event
    logger.info('Reset Request (%s) accepted by %s', uid, request.user.username)

    # Reset to state AVAILABLE
    record.state = Record.AVAILABLE
    record.save()

    return Response({
        'status': 'success',
        'message': 'reset request confirmed',
    })

@api_view(['POST'])
@login_required
@permission(User.SUPERVISOR)
@check_prerequisites('uid')
def reject_reset(request):
    uid = request.data['uid']

    # Fetch Elector
    try:
        record = Record.objects.get(student_id=uid)

    except Record.DoesNotExist:
        logger.error('student (%s) not found', uid)
        return error('student_not_found')

    # Checking elector state
    if record.state != Record.RESETTING:
        logger.info('reset request (%s) not found', uid)
        return error('reset_request_not_found')

    # Log this event
    logger.info('Reset request (%s) rejected by %s', uid, request.user.username)

    # Reset to state AVAILABLE
    record.state = Record.UNAVAILABLE
    record.save()

    return Response({
        'status': 'success',
        'message': 'reset request rejected',
    })

