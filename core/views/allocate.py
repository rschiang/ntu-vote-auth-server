import logging
from .generics import BaseElectionView
from core.exceptions import SessionInvalid
from core.serializers import VerifySerializer
from core.services import vote
from core.models import Session
from rest_framework.response import Response

logger = logging.getLogger('vote')

class AllocateView(BaseElectionView):
    """
    Confirms the authenticated information, requests an auth code and allocates it to a booth.
    """
    serializer = VerifySerializer

    def post(self, request, *args, **kwargs):
        # Sanitize input
        station = request.user.station
        validated_data = self.get_validated_data(request)

        # Load the session and check its status
        student_id = validated_data['student_id']
        session = validated_data['session']

        # 1) Request should be from same station (assert the same election)
        if session.station != station:
            logger.warning('Station mismatch for session #%s [S%s → %s]', session.id, session.station_id, station.id)
            raise SessionInvalid

        # 2) State should be AUTHENTICATED (first try) or AUTHORIZED (retries)
        elif session.state not in (Session.AUTHENTICATED, Session.AUTHORIZED):
            logger.warning('State mismatch for session #%s [S%s] (%s)', session.id, station.id, session.state)
            raise SessionInvalid

        # Since station staff could invoke this method multiple times before
        # a booth is allocated, we'll need to put reentry in mind.

        # Check if an auth code has been issued before
        if not session.auth_code:
            logger.info('Request auth code for student %s', student_id)

            # Ask the vote system to generate one for us
            ballot_ids = [ballot.foreign_id for ballot in session.ballots.all()]
            auth_code = vote.request_auth_code(ballot_ids=ballot_ids)

            # Update the session state in advance
            session.auth_code = auth_code
            session.save_state(Session.AUTHORIZED)

        logger.info('Allocate booth for student %s at station %s', student_id, station.id)

        # We've got an auth code, now try allocating a booth for elector
        # let underlying APIException do the out-of-booth handling for us
        booth_id = vote.allocate_booth(station_id=station.foreign_id, auth_code=session.auth_code)

        logger.info('Booth allocated at station %s number %s', station.id, booth_id)

        # Mark the session as VOTING
        session.save_state(Session.VOTING)

        return Response({
            'status': 'success', 'booth_id': booth_id,
        })
