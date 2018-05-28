import logging
from .generics import BaseElectionView
from core.serializers import VerifySerializer
from core.services import vote
from core.models import Session
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

logger = logging.getLogger('vote')

class AllocateView(BaseElectionView):
    """
    Confirms the authenticated information, requests an auth code and allocates it to a booth.
    """

    def post(self, request):
        # Sanitize input
        election = self.get_object()
        station = request.user.station
        serializer = VerifySerializer(data=request.data)

        try:
            # Verify the fields first
            serializer.is_valid(raise_exception=True)

            # Read validated data
            student_id = serializer.validated_data['student_id']
            session_key = serializer.validated_data['session_key']

            # Load the session and check its status
            session = Session.objects.filter(student_id=student_id, session_key=session_key).order_by('-created').first()

            # 1) Session should exist
            if not session:
                raise ValidationError(code='session_invalid')

            # 2) Request should be from same station
            elif session.station != station:
                logger.warning('Station mismatch for session #%s [S%s → %s]', session.id, session.station_id, station.id)
                raise ValidationError('session_invalid')

            # 3) State should be AUTHENTICATED (first try) or AUTHORIZED (retries)
            elif session.state not in (Session.AUTHENTICATED, Session.AUTHORIZED):
                logger.warning('State mismatch for session #%s [S%s] (%s)', session.id, station.id, session.state)
                raise ValidationError('session_invalid')

        except ValidationError:
            logger.warning('Station %s request invalid', station.id)
            logger.info(serializer.initial_data)
            raise   # Exception handler will handle for us.

        # Since station staff could invoke this method multiple times before
        # a booth is allocated, we'll need to put reentry in mind.

        # Check if an auth code has been issued before
        if not session.auth_code:
            # Ask the vote system to generate one for us
            ballot_ids = [ballot.foreign_id for ballot in session.ballots.all()]
            auth_code = vote.request_auth_code(ballot_ids=ballot_ids)

            # Update the session state in advance
            session.auth_code = auth_code
            session.save_state(Session.AUTHORIZED)

        # We've got an auth code, now try allocating a booth for elector
        # let underlying APIException do the out-of-booth handling for us
        booth_id = vote.allocate_booth(station_id=station.foreign_id, auth_code=session.auth_code)

        # Mark the session as VOTING
        session.save_state(Session.VOTING)

        return Response({
            'status': 'success', 'booth_id': booth_id,
        })
