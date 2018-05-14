from account.models import User, Session
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

    current_time = timezone.now()
    station_id = None

    # Expire older sessions
    if user.kind == User.STATION:
        station = user.station
        sessions = Session.objects.filter(user=user, expired_on__gte=current_time).order_by('created_on')
        if len(sessions) >= station.max_sessions:
            old_session = sessions.first()
            old_session.expired_on = current_time
            old_session.save()
        name = station.name
        station_id = station.external_id

    else:
        # ADMIN and SUPERVISOR
        old_sessions = Session.objects.filter(user=user, expired_on__gte=current_time)
        for s in old_sessions:
            s.expired_on = current_time
            s.save()
        name = username

    # Issue session token
    session = Session.generate(user=user)
    session.save()

    return Response({
        'status': 'success',
        'name': name,
        'station_id': 0 if station_id is None else station_id,
        'token': session.token,
    })
