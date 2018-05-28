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

    def post(self, request):
        election = self.get_object()
        serializer = VoteEventSerializer(data=request.data)

        try:
            # Sanitize and find the matching session with the auth code
            serializer.is_valid(raise_exception=True)
            auth_code = serializer.validated_data['auth_code']
            session = Session.objects.get(election=election, auth_code=auth_code, state=Session.VOTING)

        except ValidationError:
            # Seriously? With only one argument?
            logger.error('Invalid request from vote server')
            raise

        except Session.DoesNotExist:
            # Invalid auth code
            logger.error('Invalid auth code %s passed from vote server', auth_code)
            raise ValidationError(code='code_invalid')

        # Update session status
        logger.info('Student %s has voted', session.student_id)
        session.save_state(Session.VOTED)

        return Response({
            'status': 'success',
        })
