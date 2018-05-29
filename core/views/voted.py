import logging
from .generics import BaseElectionEventView
from core.models import Session
from core.serializers import VoteEventSerializer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

logger = logging.getLogger('vote.event')

class VotedEventView(BaseElectionEventView):
    """
    Called when elector has completed voting session on vote system.
    """
    serializer_class = VoteEventSerializer

    def post(self, request, *args, **kwargs):
        election = self.get_object()
        validated_data = self.get_validated_data(request)

        auth_code = validated_data['auth_code']

        try:
            session = Session.objects.get(election=election, auth_code=auth_code, state=Session.VOTING)
        except Session.DoesNotExist:
            # Invalid auth code
            logger.error('Invalid auth code %s passed from vote server', auth_code)
            raise ValidationError(code='code_invalid', detail='Auth code or state invalid.')

        # Update session status
        logger.info('Student %s has voted', session.student_id)
        session.save_state(Session.VOTED)

        return Response({
            'status': 'success',
        })
