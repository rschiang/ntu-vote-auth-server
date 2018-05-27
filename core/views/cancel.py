import logging
from .generics import BaseElectionView
from core.serializers import VerifySerializer
from core.models import Session
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

logger = logging.getLogger('vote')

class CancelView(BaseElectionView):
    """
    Rejects the authenticated information or cancel booth allocation if an auth code were issued.
    """

    def post(self, request):
        # Sanitize input
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
            logger.warning('Station %s request invalid (student %s session %s)',
                           station.id, serializer.student_id, serializer.session_key)
            raise   # Exception handler will handle for us.

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
