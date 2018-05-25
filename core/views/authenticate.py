from .generics import BaseElectionView
from .utils import error, logger
from core.serializers import AuthenticateSerializer
from core.services import aca, ExternalError
from core.models import Session
from django.conf import settings
from rest_framework.response import Response
from rest_framework.serializers import ValidationError


class AuthenticateView(BaseElectionView):
    """
    Authenticates card information against ACA API and returns available ballots.
    """

    def post(self, request):
        # Sanitize input
        station = request.user.station
        serializer = AuthenticateSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            logger.warning('Station %s request invalid (card %s [%s][%s])',
                           station.id, serializer.internal_id, serializer.student_id, serializer.revision)
            raise

        # Read validated data and authenticate against ACA
        internal_id = serializer.validated_data['internal_id']
        student_id = serializer.validated_data['student_id']
        revision = serializer.validated_data['revision']

        # Authentication methods:
        # 1) internal + student ID ["strict" mode]
        # 2) internal ID only ["quirk" mode] (for less capable NFC clients)
        # 3) student ID only (rely on client side validation)

        # Log the request first
        if settings.CARD_VALIDATION_QUIRK:
            logger.info('Station %s requests card (%s****)', station.id, internal_id[:4])
        else:
            logger.info('Station %s requests card %s[%s]', student_id, revision)

        # Call corresponding ACA API
        try:
            if not settings.CARD_VALIDATION_OFF:
                info = aca.to_student_id(internal_id)   # Use internal ID to authenicate

                # Double check if student ID matches in strict mode
                if settings.CARD_VALIDATION_STRICT and info.id != student_id:
                    logger.warning('ID %s returned instead', info.id)
                    return error('card_suspicious')

            else:
                info = aca.query_student(student_id)    # Query student ID instead

        except ExternalError as e:
            # Connection related error, fail early
            if e.reason == 'external_server_down':
                logger.exception('Failed to connect to ACA server')
                return error('external_error')

            # Authentication error
            # TODO: Tell clients the exact reason of error
            return error('card_invalid')

        # Check previous sessions for state recovery
        sessions = Session.objects.filter(student_id=student_id)
        if sessions.filter(state__in=(Session.VOTING, Session.VOTED)).exists():
            return error('duplicate_entry')

        # TODO: Determine and return available ballots
        return Response({
            'status': 'success',
        })
