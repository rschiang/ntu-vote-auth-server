import logging
import requests
from .errors import NotImplemented
from django.conf import settings

def request_auth_code(ballots):
    raise NotImplemented

def allocate_booth(station_id, auth_code):
    raise NotImplemented
