import logging
from .generics import BaseElectionView
from core.exceptions import APIException
# from core.models import Session
from core.serializers import AbortSerializer
# from core.services import vote
# from rest_framework.response import Response

logger = logging.getLogger('vote')

class AbortView(BaseElectionView):
    """
    Aborts the voting process in a booth.
    """
    serializer_class = AbortSerializer

    def post(self, request, *args, **kwargs):
        # Sanitize input
        station = request.user.station
        validated_data = self.get_validated_data(request)
        booth_id = validated_data['booth_id']

        # Call the abort API
        # vote.abort_booth(station_id=station.foreign_id, booth_id=booth_id)

        # Update the session state
        # session = Session.objects.filter(election=election, station=station, booth_id=booth_id)

        # Currently we don't record booth ID, so there are no way we could handle
        # abortion process and set the session state to Session.ABORTED properly.

        # A better way to do this is to memorize session key in the client even
        # after allocation completed; or to require station staff to manually enter
        # session key obtained from EREC control center as a safety mechanism.

        # For now we'll just disable this API all together, but we might revisit
        # this decision and add necessary fields in the future.

        logger.error('Abort not implemented')
        raise APIException(code='not_implemented')
