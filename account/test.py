from django.conf import settings
from account.models import User, Station, Session

from rest_framework.test import APIClient, APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status


class RegisterTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.username = 'station1'
        self.password = 'station1'
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.name = 'NTU'
        self.station = Station()
        self.station.name = self.name
        self.station.user = self.user
        self.station.external_id = 1
        self.station.max_sessions = 3
        self.station.save()

        self.url = reverse('register')

    def test_register_success(self):
        """
        test case for station login
        """
        self.user.kind = User.STATION
        self.user.save()

        # Assure config is correct
        user = User.objects.get(username=self.username)
        self.assertEqual(user.username, self.username)
        self.assertEqual(True, user.check_password(self.password))

        # Testing Data
        data = {'username': self.username, 'password': self.password,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        response = self.client.post(self.url, data)

        # Get session object
        try:
            session = Session.objects.get(user=self.user)
        except:
            session = None

        self.assertEqual(response.data, {
            'status': 'success',
            'name': self.station.name,
            'station_id': self.station.external_id,
            'token': session.token,
        })


class PingTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.username = 'station1'
        self.password = 'station1'
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.kind = User.STATION
        self.user.save()

        self.name = 'NTU'
        self.station = Station()
        self.station.name = self.name
        self.station.user = self.user
        self.station.external_id = 1
        self.station.max_sessions = 3
        self.station.save()

        self.url = reverse('ping')
        # login
        data = {'username': self.username, 'password': self.password,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        client = APIClient()
        client.post(reverse('register'), data, format='json')

        try:
            session = Session.objects.get(user=self.user)
        except:
            session = None
        self.session = session
        self.token = session.token

    def test_ping_success(self):
        data = {'token': self.token,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        response = self.client.post(self.url, data)
        self.assertEqual(response.data['status'], 'success')

    def test_null_station_id(self):
        username = 'station2'
        password = 'station2'
        user = User(username=username)
        user.set_password(password)
        user.kind = User.STATION
        user.save()

        station = Station()
        station.name = 'no name'
        station.user = user
        station.max_sessions = 3
        station.save()
        # login
        data = {'username': username, 'password': password,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        client = APIClient()
        client.post(reverse('register'), data, format='json')

        try:
            session = Session.objects.get(user=user)
        except:
            session = None

        data = {'token': session.token,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        response = self.client.post(self.url, data)
        self.assertEqual(response.data, {'status': 'error', 'reason': 'station_error'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
