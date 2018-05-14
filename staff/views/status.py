from core.models import AuthCode
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import scheduled, login_required, permission
from account.models import User, Station, Session
from core.views.utils import logger


@api_view(['POST'])
@scheduled
@login_required
@permission(User.ADMIN, User.SUPERVISOR)
def status(request):
    current_time = timezone.now()
    return Response({
        'status': 'success',
        'ballot': {
            'used': AuthCode.objects.filter(issued=True).count(),
            'remain': AuthCode.objects.filter(issued=False).count()
        },
        'stations': [{
            'name': s.name,
            'id': s.external_id,
            'status': str(Session.objects.filter(user=s.user, expired_on__gte=current_time).order_by('last_seen').last().last_seen)
        } for s in Station.objects.exclude(external_id__isnull=True)],
    })
