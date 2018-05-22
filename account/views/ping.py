from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class PingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        current_time = timezone.now()
        # TODO: Insert telemetry here
        return Response({'status': 'success', 'timestamp': current_time.isoformat()})
