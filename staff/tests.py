from django.conf import settings
from account.models import User, Station, Session

from rest_framework.test import APIClient, APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status

