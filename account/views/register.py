from account.models import User, Session, Station
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import check_prerequisites
from core.views.utils import error, logger

@api_view(['POST'])
@check_prerequisites('username', 'password')
def register(request):
    username = request.data['username']
    password = request.data['password']

    # Authentication
    user = None
    try:
        user = User.objects.get(username=username)
        if not user.check_password(password):
            user = None
        elif not user.is_active:
            logger.error('Login attempt failed for deactivated user %s', username)
            return error('unauthorized', status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        pass

    # Filter and log failed attempts
    if not user:
        logger.error('Login attempt failed for "%s":"%s"', username, password)
        return error('unauthorized', status=status.HTTP_401_UNAUTHORIZED)

    # Authorization, check user identity type
    if not user.kind == User.STATION or not user.station.is_active:
        logger.error('User %s improperly attempted to register session', username)
        return error('forbidden', status=status.HTTP_403_FORBIDDEN)

    # Expire older sessions
    station = user.station
    current_time = timezone.now()
    sessions = Session.objects.filter(station=station, expired_on__gte=current_time).order_by('created_on')
    if len(sessions) >= station.max_sessions:
        old_session = sessions.first()
        old_session.expired_on = current_time
        old_session.save()

    # Issue session token
    session = Session.generate(station=station)
    session.save()

    return Response({
        'status': 'success',
        'station': station.external_id or station.id,
        'name': station.name,
        'token': session.token,
    })
