import logging
import requests
from ..errors import ExternalError
from django.conf import settings
from xml.etree import ElementTree as et

logger = logging.getLogger('vote.aca')

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
            self.entity = et.fromstring(response.text)
        except (UnicodeDecodeError, et.ParseError) as e:
            logger.exception('Failed to load server entity')
            raise ExternalError(code='entity_malformed') from e

    def __getitem__(self, key):
        ele = self.entity.find(key.upper())
        if ele is None:
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
