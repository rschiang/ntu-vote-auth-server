import logging
from .generics import BaseElectionView
from core.exceptions import AlreadyVoted, CardInvalid, ElectorBanned, ElectorSuspicious, NotQualified
from core.serializers import AuthenticateSerializer
from core.services import aca, AuthenticationError
from core.models import Ballot, Elector, Session
from django.conf import settings
from rest_framework.response import Response

logger = logging.getLogger('vote')

class AuthenticateView(BaseElectionView):
    """
    Authenticates card information against ACA API and returns available ballots.
    """
    serializer_class = AuthenticateSerializer

    def post(self, request, *args, **kwargs):
        # Sanitize input
        election = self.get_object()
        station = request.user.station
        validated_data = self.get_validated_data(request)

        # Read validated data and authenticate against ACA
        internal_id = validated_data['internal_id']
        student_id = validated_data['student_id']
        revision = validated_data['revision']

        # Prepare the session
        session = Session.objects.create(election=election, station=station, student_id=student_id, revision=revision)

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
                    session.save_state(Session.NOT_AUTHENTICATED)
                    raise ElectorSuspicious

            else:
                student_id_with_rev = student_id + str(revision)
                info = aca.query_student(student_id_with_rev)    # Query student ID instead

        # Error handling
        # We don't catch ExternalError as we can do nothing about it.
        except AuthenticationError as e:
            session.save_state(Session.NOT_AUTHENTICATED)
            code = e.get_codes()
            if code == 'card_invalid':
                raise CardInvalid
            else:   # Let ACA error codes pass through
                raise ElectorSuspicious(code=code)

        # Now that ACA has verified the elector,
        # we'll check against our record if there were any previous voting sessions.
        sessions = Session.objects.filter(student_id=student_id)

        # 1) Check if the elector has voted or not
        if sessions.filter(state__in=(Session.VOTING, Session.VOTED, Session.REMOTE_VOTED)).exists():
            session.save_state(Session.NOT_AUTHENTICATED)
            raise AlreadyVoted
        # 2) Check if the elector was banned (either by registering remote voting
        # or earlier unlawful attempts.)
        elif sessions.filter(state__in=(Session.ABORTED, Session.BANNED)).exists():
            session.save_state(Session.NOT_AUTHENTICATED)
            raise ElectorBanned

        # 3) Iterate through previous records, cancel out incomplete sessions;
        # double-check on previous information if available.
        for old_session in sessions.order_by('created'):
            # Check on previous revision record; reject if using an older one.
            if old_session.revision > revision:
                session.save_state(Session.NOT_AUTHENTICATED)
                raise ElectorSuspicious

            # Cancel out older sessions
            if old_session.state in (Session.AUTHORIZED, Session.CANCELED):
                # Session terminated before booth allocation.
                if old_session.state == Session.AUTHORIZED:
                    logger.info('Expiring session #%s [S%s] (2 → Z)', old_session.id, old_session.station.id)
                    old_session.save_state(Session.CANCELED)
                else:
                    logger.info('Found old canceled session #%s [S%s]', old_session.id, old_session.station.id)

                # Since the elector has confirmed their identity and we've already
                # requested an auth code based on that, no re-evaluation would be done.
                # We'll just return cached identities instead.
                ballots = old_session.ballots.all()
                session.auth_code = old_session.auth_code
                session.save_state(Session.AUTHENTICATED)
                session.ballots.add(*ballots)

                return Response({
                    'status': 'success', 'session_key': session.key, 'cached': True,
                    'college': info.college, 'department': info.department,
                    'ballots': [ballot.name for ballot in ballots],
                })

            elif old_session.state == Session.AUTHENTICATED:
                # Session terminated before confirming identity.
                # No big deal. We'll just invalidate this session.
                logger.info('Expiring session #%s [S%s] (1 → Y)', old_session.id, old_session.station.id)
                old_session.save_state(Session.NOT_VERIFIED)

            elif old_session.state != Session.NOT_AUTHENTICATED:
                # Either we've bumped into CREATED or some unknown state.
                # Shouldn't occur but we'll cancel it out anyway.
                logger.warning('Expiring session #%s [S%s] (%s → X)', old_session.id, old_session.station.id, old_session.state)
                old_session.save_state(Session.NOT_AUTHENTICATED)

        #
        # ...Authentication succeeded.

        # Build up elector information for condition matching
        student_type = info.id[0]
        elector_data = {
            # Known information
            'type': student_type, 'college': info.college_id, 'department': info.department,
            # Normalized information
            'standing': ('R' if student_type in settings.GRADUATE_CODE else
                         ('B' if student_type in settings.UNDERGRADUATE_CODE else '')),
        }

        # Filter out ineligible identities as regulated in Election & Recall Act §13(2).
        if student_type not in settings.GENERAL_CODE:
            logger.warning('Student %s does not qualify as elector', student_id)
            session.save_state(Session.NOT_AUTHENTICATED)
            raise NotQualified

        # Iterate through ballots and check eligibility
        ballots = []
        for ballot in Ballot.objects.all_ballots(election=election):
            # 1) Check if the elector is explicitly specified in list.
            # Takes presedence over all ballot conditions.
            try:
                elector = ballot.electors.get(student_id=student_id)
                if elector.is_allowed:
                    ballots.append(ballot)
                continue
            except Elector.DoesNotExist:
                pass    # This elector isn't explicitly black/whitelisted. Good.

            # 2) Matches the elector data against ballot conditions.
            # We've done the logic on models, so just call the method.
            if ballot.match(fields=elector_data):
                ballots.append(ballot)

        # 3) Checks if there is at least one ballot to vote.
        if not ballots:
            logger.warning('Student %s does not qualify any ballot', student_id)
            session.save_state(Session.NOT_AUTHENTICATED)
            raise NotQualified  # Fail if there aren't any

        # Saves the session and intermediate information
        session.ballots.add(*ballots)
        session.save_state(Session.AUTHENTICATED)

        # Returns the ballot information and the session key for further operation
        return Response({
            'status': 'success', 'session_key': session.key,
            'college': info.college, 'department': info.department,
            'ballots': [ballot.name for ballot in ballots],
        })
