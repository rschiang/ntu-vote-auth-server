from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import login_required, permission
from account.models import User


@api_view(['POST'])
@login_required
@permission(User.ADMIN, User.STATION, User.SUPERVISOR)
def ping(request):
    current_time = timezone.now()
    return Response({'status': 'success', 'timestamp': current_time.isoformat()})
