import logging
import requests
from .errors import NotImplemented
from django.conf import settings

logger = logging.getLogger('vote.ext')

def fetch_booth_status(station_id):
    raise NotImplemented

def request_auth_code(ballots):
    raise NotImplemented

def allocate_booth(station_id, auth_code):
    raise NotImplemented

def abort_booth(station_id, booth_id):
    raise NotImplemented
