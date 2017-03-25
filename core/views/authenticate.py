import re
from core import service
from core.models import Record, AuthToken, OverrideEntry, Entry
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from urllib.error import URLError
from .decorators import check_prerequisites, scheduled, login_required, permission
from .utils import error, logger
from account.models import User


@api_view(['POST'])
@scheduled
@login_required
@permission(User.STATION)
@check_prerequisites('cid', 'uid')
def authenticate(request):
    # Check parameters
    internal_id = request.data['cid']
    raw_student_id = request.data['uid']
    station_id = request.station

    if settings.ENFORCE_CARD_VALIDATION:
        # Parse student ID
        if re.match(r'[A-Z]\d{2}[0-9A-Z]\d{6}', raw_student_id) and re.match(r'[0-9a-f]{8}', internal_id) and re.match(r'\d+', station_id):
            # Extract parameters
            student_id = raw_student_id[:-1]
            revision = int(raw_student_id[-1:])
            logger.info('Station %s request for card %s[%s]', station_id, student_id, revision)
        else:
            # Malformed card information
            logger.info('Station %s request for card %s (%s)', station_id, raw_student_id, internal_id)
            return error('card_invalid')

    else:
        # Do not reveal full internal ID as ACA requested
        logger.info('Station %s request for card (%s****)', station_id, internal_id[:4])

    # Call ACA API
    try:
        aca_info = service.to_student_id(internal_id)

    except URLError:
        logger.exception('Failed to connect to ACA server')
        return error('external_error', status.HTTP_502_BAD_GATEWAY)

    except service.ExternalError as e:
        if not settings.ENFORCE_CARD_VALIDATION:
            # We can only reveal full internal ID if it’s an invalid card
            logger.exception('Card rejected by ACA server (%s), reason %s', internal_id, e.reason)
        else:
            logger.exception('Card rejected by ACA server, reason %s', e.reason)

        # Tell clients the exact reason of error
        if e.reason == 'card_invalid' or e.reason == 'student_not_found':
            return error('card_invalid')
        elif e.reason == 'card_blacklisted':
            return error('card_suspicious')
        return error('external_error', status.HTTP_502_BAD_GATEWAY)

    else:
        if not settings.ENFORCE_CARD_VALIDATION:
            student_id = aca_info.id
            revision = 0
            logger.info('User %s (%s) checked', student_id, aca_info.type)
        elif aca_info.id != student_id:
            logger.info('ID %s returned instead', aca_info.id)
            return error('card_suspicious')

    # Check vote record
    try:
        record = Record.objects.get(student_id=student_id)
        if settings.ENFORCE_CARD_VALIDATION and record.revision != revision:
            # ACA claim the card valid!
            logger.info('Expect revision %s, recorded %s', revision, record.revision)
            return error('card_suspicious')

        if record.state == Record.VOTING:
            # Automaticlly unlock stuck record
            record.state = Record.AVAILABLE
            record.save()
            logger.info('Reset %s state from VOTING', student_id)

        if record.state != Record.AVAILABLE:
            logger.error('Duplicate entry (%s)', student_id)
            return error('duplicate_entry')

    except Record.DoesNotExist:
        record = Record(student_id=student_id, revision=revision)

    # Determine graduate status
    kind = None
    try:
        entry = Entry.objects.get(dpt_code=aca_info.department)
        kind = entry.kind
        logger.debug('DPT_CODE %s', type(aca_info.department))
    except Entry.DoesNotExist:
        logger.error('Entry not found: %s', aca_info.department)
        return error('entry_not_found')

    try:
        override = OverrideEntry.objects.get(student_id=student_id)
        kind = override.kind
    except OverrideEntry.DoesNotExist:
        pass

    if kind is None:
        return error('unqualified')

    # Generate record and token
    record.state = Record.LOCKED
    record.save()

    token = AuthToken.generate(student_id, station_id, kind)
    token.save()

    logger.info('Auth token issued: %s', token.code)
    return Response({'status': 'success', 'uid': student_id, 'type': aca_info.college, 
        'college': settings.DPTCODE_NAME[aca_info.department], 'vote_token': token.code})
