from core.models import CooperativeMember
from django.conf import settings
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as et

def is_coop_member(student_id):
    return CooperativeMember.objects.filter(student_id=student_id).exists()

def to_student_id(internal_id):
    # Build up the clumsy request entity
    req_entity = et.Element('STUREQ')
    req_uid = et.SubElement(req_entity, 'UID')
    req_uid.text = settings.ACA_API_USER
    req_pass = et.SubElement(req_entity, 'PASSWORD')
    req_pass.text = settings.ACA_API_PASSWORD
    req_cid = et.SubElement(req_entity, 'CARDNO')
    req_cid.text = internal_id
    req_data = et.tostring(req_entity, encoding='big5')

    # Initiate HTTP request
    request = Request(settings.ACA_API_URL, method='POST')
    request.add_header('Content-Type', 'application/xml')
    request.add_header('X-Requested-With', 'NTUVote')

    # Load and parse response
    try:
        response = urlopen(request, data=req_data)
        resp_data = response.read().decode('big5')
        resp_entity = et.fromstring(resp_data)
    except (UnicodeDecodeError, et.ParseError):
        raise ExternalError('entity_malformed')

    # Read the response entity
    try:
        status = resp_entity.find('WEBOK').text
        error = resp_entity.find('ERROR').text

        if status != 'OK':
            raise ExternalError(error)

        info = StudentInfo()
        info.id = resp_entity.find('STUID').text
        info.type = resp_entity.find('STUTYPE').text
        info.valid = resp_entity.find('INCAMPUS').text
        info.college = resp_entity.find('COLLEGE').text

    except AttributeError:
        raise ExternalError('entity_malformed')

    return info

class StudentInfo(object):

    def __init__(self, id=None, type=None, valid=False, college=None):
        self.id = id
        self.type = type
        self.valid = valid
        self.college = college

class ExternalError(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return repr(self.reason)
