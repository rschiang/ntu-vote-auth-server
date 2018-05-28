from account.permissions import IsStationStaff
from core.services import vote
from rest_framework.views import APIView
from rest_framework.response import Response

class BoothView(APIView):
    """
    Gets the status of each booth in a voting station.
    """
    permission_classes = (IsStationStaff,)

    def get(self, request):
        station = request.user.station

        # TODO: Fetch status from vote system
        response = vote.fetch_booth_status(station.foreign_id)

        return Response({
            'status': 'success',
            'response': response,
        })
