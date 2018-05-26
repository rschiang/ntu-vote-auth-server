import logging
import requests
import struct
from .errors import AuthenticationError, ExternalError
from django.conf import settings
from xml.etree import ElementTree as et

logger = logging.getLogger('vote.aca')


def reverse_indian(i):
    return struct.unpack('<I', struct.pack('>I', i))


def query_student(student_id):
    """
    Gets the relevant student information from ACA.
    """
    # Loads the response from ACA
    request = AcaRequest(stuid=student_id)
    response = request.post('stuinfo2ByStuId')

    # Read the response entity
    try:
        if not response.ok:
            error = response.error
            logger.warning('Querying ACA failed: %s', error)
            raise ExternalError(detail=error)  # TODO: Determine error type
        info = StudentInfo(id=student_id, entity=response)
    except KeyError:
        logger.exception('Server entity malformed')
        raise ExternalError(code='entity_malformed')

    logger.info(str(info))
    return info


def to_student_id(internal_id):
    """
    Gets the student ID and relevant information associated with this card from ACA.
    """
    # Build the request
    serial_id = str(reverse_indian(int(internal_id, 16))[0])
    request = AcaRequest(cardno=serial_id)

    # Load and parse response
    response = request.post('stuinfo2ByCardno')

    # Read the response entity
    try:
        if not response.ok:
            error = response.error
            logger.warning('Querying ACA failed: %s', error)

            if '為黑名單' in error:
                raise AuthenticationError(code='card_blacklisted')
            elif '在卡務中不存在' in error or '尚未啟用' in error:
                raise AuthenticationError(code='card_invalid')
            elif '查無學號資料' in error:
                raise AuthenticationError(code='student_not_found')
            elif '未授權' in error:
                raise ExternalError(code='unauthorized')
            elif '輸入資料錯誤' in error:
                raise ExternalError(code='params_invalid')

            # All other rare cases
            raise ExternalError(detail=error)

        info = StudentInfo(entity=response)

    except KeyError:
        logger.exception('Server entity malformed')
        raise ExternalError(code='entity_malformed')

    logger.info(str(info))
    return info


class AcaRequest(object):
    """
    Builds and sends an ACA-style API request.
    """

    def __init__(self, **values):
        self.values = values

    def post(self, method):
        """
        Sends the request, returns an AcaResponse object.
        """

        # Prepare parameters
        values = self.values
        values['uid'] = settings.ACA_API_USER
        values['password'] = settings.ACA_API_PASSWORD

        # Generate POST entity
        entity = et.Element('STUREQ')
        ele = et.SubElement(entity, 'Vers')  # dunno why this is different
        ele.text = '1.00'
        for key, value in values.items():
            ele = et.SubElement(entity, key.upper())
            ele.text = value
        data = et.tostring(entity, encoding='big5')

        # Builds and sends the HTTP request
        url = settings.ACA_API_URL.format(method)
        headers = {
            'Content-Type': 'text/xml; charset=big5',
            'X-Requested-With': 'NTUVote',
        }

        try:
            response = requests.post(url, data=data, headers=headers)
        except Exception as e:
            logger.exception('Failed to connect the ACA server')
            raise ExternalError(code='external_server_down') from e

        return AcaResponse(response)


class AcaResponse(object):
    """
    Contains the response from an ACA-style API request.
    """

    def __init__(self, response):
        response.encoding = 'big5'
        try:
            self.entity = et.fromstring(response.body)
        except (UnicodeDecodeError, et.ParseError) as e:
            logger.exception('Failed to load server entity')
            raise ExternalError(code='entity_malformed') from e

    def __getitem__(self, key):
        ele = self.entity.find(key.upper())
        if not ele:
            raise KeyError
        return ele.text

    @property
    def ok(self):
        """
        Returns True if the request status is set to 'OK'; False otherwise.
        """
        return self['webok'] == 'OK'

    @property
    def error(self):
        """
        Returns the error text.
        """
        return self['error']


class StudentInfo(object):
    """
    Contains student information acquired from ACA.
    """

    def __init__(self, id=None, type=None, valid=False, college=None, department=None, entity=None):
        # TODO: Normalize ACA input
        self.id = id or entity['stuid']
        self.type = type or entity['stutype']  # chinese value returned from ACA server
        self.valid = valid or (entity['incampus'] == 'true')
        self.college = college or entity['college']
        self.department = department or entity['dptcode']

    def __repr__(self):
        return "{0}(id='{id}', type='{type}', valid={valid}, college='{college}', department='{department}')".format(self.__class__.__name__, **self.__dict__)

    def __str__(self):
        return '<StudentInfo: {id} ({college} {type} {department}){0}>'.format('' if self.valid else '*', **self.__dict__)
