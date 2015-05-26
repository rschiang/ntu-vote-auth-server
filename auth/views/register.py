from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import check_prerequisites
from core.views.utils import error, logger
from .models import User, Session

@api_view(['POST'])
@check_prerequisites('username', 'password')
def register(request):
    username = request.POST['username']
    password = request.POST['password']

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
    if not user.kind == User.STATION or not user.station or not user.station.is_active:
        logger.error('User %s improperly attempted to register session', username)
        return error('forbidden', status=status.HTTP_403_FORBIDDEN)

    # Issue session token
    session = Session.generate(station=user.station)
    session.save()

    return Response({
        'status': 'success',
        'station': user.station.external_id or user.station.id,
        'name': user.station.name,
        'token': session.token,
    })
