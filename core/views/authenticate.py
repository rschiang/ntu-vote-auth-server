import re
from core import service
from core.models import Record, AuthToken, OverrideEntry
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from urllib.error import URLError
from .decorators import check_prerequisites, scheduled
from .utils import error, logger

@api_view(['POST'])
@scheduled
@check_prerequisites('cid', 'uid', 'station')
def authenticate(request):
    # Check parameters
    internal_id = request.DATA['cid']
    raw_student_id = request.DATA['uid']
    station_id = request.DATA['station']

    # Parse student ID
    if re.match(r'[A-Z]\d{2}[0-9A-Z]\d{6}', raw_student_id) and re.match(r'[0-9a-f]{8}', internal_id) and re.match(r'\d+', station_id):
        # Extract parameters
        student_id = raw_student_id[:-1]
        revision = int(raw_student_id[-1:])
        logger.info('Station %s request for card %s[%s]', station_id, student_id, revision)
    else:
        logger.info('Station %s request for card %s (%s)', station_id, raw_student_id, internal_id)
        return error('card_invalid')

    # Call ACA API
    try:
        aca_info = service.to_student_id(internal_id)

    except URLError:
        logger.exception('Failed to connect to ACA server')
        return error('external_error', status.HTTP_502_BAD_GATEWAY)

    except service.ExternalError as e:
        logger.exception('Card rejected by ACA server, reason %s', e.reason)
        if e.reason == 'card_invalid' or e.reason == 'student_not_found':
            return error('card_invalid')
        elif e.reason == 'card_blacklisted':
            return error('card_suspicious')
        return error('external_error', status.HTTP_502_BAD_GATEWAY)

    else:
        if aca_info.id != student_id:
            logger.info('ID %s returned instead', aca_info.id)
            return error('card_suspicious')

    # Check vote record
    try:
        record = Record.objects.get(student_id=student_id)
        if record.revision != revision:
            # ACA claim the card valid!
            logger.info('Expect revision %s, recorded %s', revision, record.revision)
            return error('card_suspicious')

        if record.state != Record.AVAILABLE:
            return error('duplicate_entry')

    except Record.DoesNotExist:
        record = Record(student_id=student_id, revision=revision)

    # Build up kind identifier
    try:
        college = settings.COLLEGE_IDS[aca_info.college]
    except KeyError:
        # Use student ID as an alternative
        logger.warning('No matching college for ACA entry %s', aca_info.college)
        college = student_id[3]

        # In rare cases, we may encounter students without colleges
        if college not in settings.COLLEGE_NAMES:
            logger.warning('No matching college for ID %s', college)
            college = '0'

    # Determine graduate status
    type_code = student_id[0]
    kind = college
    try:
        override = OverrideEntry.objects.get(student_id=student_id)
        kind = override.kind
    except OverrideEntry.DoesNotExist:
        if type_code in settings.GRADUATE_CODES:
            kind += '1'
        elif type_code in settings.UNDERGRADUATE_CODES:
            # Departments who opt to join election
            if aca_info.department in ('4010', '6090', '9010'):
                kind += 'A'
            else:
                kind += '0'

    # Check if student has eligible identity
    if kind not in settings.KINDS:
        return error('unqualified')

    # Generate record and token
    record.state = Record.LOCKED
    record.save()

    token = AuthToken.generate(student_id, station_id, kind)
    token.save()

    logger.info('Auth token issued: %s', token.code)
    return Response({'status': 'success', 'uid': student_id, 'type': settings.KINDS[kind], 'token': token.code})
