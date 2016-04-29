from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import login_required


@api_view(['POST'])
@login_required
def ping(request):
    current_time = timezone.now()
    return Response({'status': 'success', 'timestamp': current_time.isoformat()})
