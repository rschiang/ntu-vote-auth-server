import logging
import requests
from .errors import ExternalError, NotImplemented, RequestNotFulfilled
from datetime import datetime
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('vote.ext')

def fetch_booth_status(station_id=None):
    """
    Returns the status of booths at the given station.
    """
    now = timezone.now()
    response = send_request('/status/all')

    # Reads and iterates through booth status
    try:
        if response['status'] == 'ok':
            # Filter by station IDs first if given
            result_list = response['result']
            if station_id:
                station_id = str(station_id)
                result_list = [i for i in result_list if i['a_id'] == station_id]

            # Iterate through entries and convert them into objects
            entries = []
            for entry in response['result']:
                # TODO: Use REST Framework serializer.
                station_id = int(entry['a_id'])
                booth_id = int(entry['num'])
                status = entry['status']
                last_seen = datetime.fromtimestamp(int(entry['lastseen']), tz=timezone.utc)

                # Determine real status based on last_seen
                if status == 'free' and (now - last_seen).total_seconds() > 60:
                    status = 'offline'
                elif status == 'lock':
                    status = 'in_use'
                else:
                    status = 'available'

                # Create corresponding booth info object
                entries.push(BoothInfo(station_id=station_id, booth_id=booth_id, status=status, last_seen=last_seen))

            # Return the whole thing
            return entries

    # Error handling
    # Either a KeyError or a status: error indicates something wrong.
    except KeyError:
        logger.exception('Server entity malformed on req #%s', response.get('api_callid'))
        raise ExternalError('entity_malformed')
    else:
        logger.error('Booth status query failed on req #%s, reason %s', response.get('api_callid'), response.get('message'))
        logger.info(response)
        raise ExternalError


def request_auth_code(ballot_ids):
    """
    Requests the vote system to generate an auth code with the given set of ballots.
    """
    response = send_request('/vote/allocate', {'kind': ','.join(ballot_ids)})

    # Reads and returns the enveloped auth code
    try:
        if response['status'] == 'ok':
            item = response['list'][0]
            auth_code = item['authcode_plain']
            logger.info('Auth code %s issued for kind %s', auth_code, item['kind'])
            return auth_code

    # Error handling
    # Either a KeyError or a status: error indicates something wrong.
    except KeyError:
        logger.exception('Server entity malformed on req #%s', response.get('api_callid'))
        raise ExternalError('entity_malformed')
    else:
        logger.error('Auth code request failed on req #%s, reason %s', response.get('api_callid'), response.get('message'))
        logger.info(response)
        raise ExternalError


def allocate_booth(station_id, auth_code):
    """
    Requests the vote system to dispatch the auth code to a vacant booth at the given station.
    """
    response = send_request('/vote/new', {'a_id': station_id, 'authcode': auth_code})

    try:
        if response['status'] == 'ok':
            # Read and return the booth ID if succeeded
            booth_id = response['num']
            logger.info('Allocated to station %s booth %s for auth code %s', station_id, booth_id, auth_code)
            return booth_id

        else:
            # Request failed, check error message and return something useful
            message = response['message']

            if 'no more online-booth-tablet' in message:
                logger.info('No booth available for station %s', station_id)
                raise RequestNotFulfilled('booth_unavailable')

            elif 'authcode step must 0' in message:
                logger.info('Auth code %s has been used', auth_code)
                raise ExternalError('auth_code_used')

            else:
                # Probably state error, note this
                logger.error('Allocate booth failed on req #%s, reason %s', response['api_callid'], message)
                raise ExternalError

    except KeyError:
        logger.exception('Server entity malformed on req #%s', response.get('api_callid'))
        raise ExternalError('entity_malformed')


def abort_booth(station_id, booth_id):
    """
    Aborts the voting process at the given booth on station staff's request.
    """
    raise NotImplemented


def send_request(path, values=None):
    """
    Helper function for sending request to vote system.
    """
    # Build HTTP request parameters, filling in API key
    url = settings.VOTE_API_URL + path
    values = values or {}
    values['apikey'] = settings.VOTE_API_KEY

    # Headers aren't necessary, but it's our taste!
    headers = {'X-Requested-With': 'NTUVote'}

    # Sends and deserializes the response.
    # Any malformed response would be caught, but not `{'status': 'error'}` ones.
    try:
        response = requests.post(url, data=values, headers=headers)
        return response.json()

    except Exception as e:
        logger.exception('Failed to connect to vote server')
        raise ExternalError(code='external_server_down') from e


class BoothInfo(object):
    """
    Contains status information for a booth.
    """

    def __init__(self, station_id=None, booth_id=None, status=None, last_seen=None):
        self.station_id = station_id
        self.booth_id = booth_id
        self.status = status
        self.last_seen = last_seen

    def __str__(self):
        return '<BoothInfo: #{station_id}-{booth_id} ({status})>'.format(**self.__dict__)
