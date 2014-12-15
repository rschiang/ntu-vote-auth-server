import re
from core import service
from core.models import Record, AuthCode
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from urllib.error import URLError

def index(request):
    return HttpResponse('It works!')

def error(reason, status=status.HTTP_400_BAD_REQUEST):
    return Response({'status': 'error', 'reason': reason}, status=status)

@api_view(['POST'])
def api(request):
    # Check parameters
    try:
        api_key = request.DATA['api_key']
        version = request.DATA['version']
        internal_id = request.DATA['cid']
        raw_student_id = request.DATA['uid']
        station_id = request.DATA['station']
    except KeyError:
        return error('params_invalid')
    else:
        # Assert API key and version match
        if api_key != settings.API_KEY:
            return error('unauthorized', status.HTTP_401_UNAUTHORIZED)
        elif version != '1':
            return error('version_not_supported')

        # Parse student ID
        if not re.match(r'[A-Z]\d{2}[0-9AB]\d{6}', raw_student_id):
            return error('card_invalid')
        else:
            student_id = raw_student_id[:-1]
            revision = int(raw_student_id[-1:])

    # Call ACA API
    try:
        aca_student_id = service.to_student_id(internal_id)
    except URLError:
        return error('server_error', status.HTTP_502_BAD_GATEWAY)
    except service.ExternalError as e:
        # TODO: Check service error
        return error('error')
    else:
        if aca_student_id != student_id:
            return error('card_suspicious')

    # Check vote record
    try:
        record = Record.objects.filter(student_id=student_id)
        if record.revision != revision:
            # ACA claim the card valid!
            return error('card_suspicious')

        if record.state != Record.AVAILABLE:
            return error('duplicate_entry')
    except Record.DoesNotExist:
        pass

    # Check if cooperative member
    is_coop = service.is_coop_member(student_id)

    # Build up kind identifier
    kind = student_id[3] + ('1' if is_coop else '0')
    kind_name = settings.KINDS[kind]

    code = AuthCode.objects.filter(kind=kind, issued=False).first()
    if code:
        entry = Record()
        entry.student_id = student_id
        entry.save()

        code.issued = True
        code.save()
    else:
        return error('out_of_auth_code', status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({"status": "success", "uid": student_id, "type": kind_name, "code": code.code})
