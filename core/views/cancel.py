import logging
from .generics import BaseElectionView
from core.exceptions import SessionInvalid
from core.serializers import VerifySerializer
from core.models import Session
from rest_framework.response import Response

logger = logging.getLogger('vote')

class CancelView(BaseElectionView):
    """
    Rejects the authenticated information or cancel booth allocation if an auth code were issued.
    """
    serializer_class = VerifySerializer

    def post(self, request, *args, **kwargs):
        # Sanitize input
        station = request.user.station
        validated_data = self.get_validated_data(request)

        # Load the session and check its status
        student_id = validated_data['student_id']
        session = validated_data['session']

        # 1) Request should be from same station (asserting the same election)
        if session.station != station:
            logger.warning('Station mismatch for session #%s [S%s → %s]', session.id, session.station_id, station.id)
            raise SessionInvalid

        # 2) State should be AUTHENTICATED (first try) or AUTHORIZED (retries)
        elif session.state not in (Session.AUTHENTICATED, Session.AUTHORIZED):
            logger.warning('State mismatch for session #%s [S%s] (%s)', session.id, station.id, session.state)
            raise SessionInvalid

        # Check if an auth code has been issued before
        if not session.auth_code:
            # No auth code has been issued so far, invalidate the session directly.
            logger.info('Rejected student %s at station %s', student_id, station.id)
            session.save_state(Session.NOT_VERIFIED)
        else:
            # Mark the session as canceled; re-authentication would return cached info.
            logger.info('Canceled vote session of student %s at station %s', student_id, station.id)
            session.save_state(Session.CANCELED)

        return Response({
            'status': 'success',
        })
