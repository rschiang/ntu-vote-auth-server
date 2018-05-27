import logging
import requests
from .errors import ExternalError, NotImplemented, RequestNotFulfilled
from django.conf import settings

logger = logging.getLogger('vote.ext')

def fetch_booth_status(station_id):
    """
    Returns the status of booths at the given station.
    """
    raise NotImplemented

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
    response = send_request('/vote/new', {'aid': station_id, 'authcode': auth_code})

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
