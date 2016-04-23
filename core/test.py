from django.conf import settings
from account.models import User, Station, Session

from rest_framework.test import APIClient, APITestCase
from django.core.urlresolvers import reverse


class CoreTestCase(APITestCase):
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
            session = Session.objects.get(station=self.station)
        except:
            session = None
        self.session = session
        self.token = session.token

    def test_authenticate_success(self):
        pass

    def test_complete_success(self):
        pass

    def test_confirm_success(self):
        pass

    def test_report_success(self):
        pass
