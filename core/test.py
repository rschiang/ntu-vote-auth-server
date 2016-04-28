from django.conf import settings
from account.models import User, Station, Session
from core.models import Record, AuthToken, AuthCode

from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.core.urlresolvers import reverse


class CoreTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.student_id = 'B03705024'

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

        self.authcode = AuthCode(kind='70', code='70-ZU2U0RAKX-KOXLUYHJI-7C05B')
        self.authcode.save()

    def test_authenticate_success(self):
        return
        url = reverse('authenticate')
        data = {'cid': 'fff', 'uid': 'B03705024',
                'station': self.station.external_id,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        response = self.client.post(url, data)
        print(response.data)

    def test_confirm_success(self):
        record = Record(student_id=self.student_id)
        record.state = Record.LOCKED
        record.save()
        token = AuthToken.generate(self.student_id, str(self.station.external_id), '70')
        token.save()

        url = reverse('confirm')
        data = {'uid': self.student_id, 'station': str(self.station.external_id), 'token': token.code,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        response = self.client.post(url, data)
        callback = 'https://{0}{1}?callback={2}'.format(
            settings.CALLBACK_DOMAIN, reverse('callback'), token.confirm_code)
        self.assertEqual(response.data, {
            'status': 'success',
            'code': self.authcode.code,
            'callback': callback,
        })

    def test_complete_success(self):
        record = Record(student_id=self.student_id)
        record.state = Record.VOTING
        record.save()
        token = AuthToken.generate(self.student_id, str(self.station.external_id), '70')
        token.save()

        url = 'https://{0}{1}?callback={2}'.format(
            settings.CALLBACK_DOMAIN, reverse('callback'), token.confirm_code)
        response = self.client.get(url)
        record = Record.objects.get(student_id=self.student_id)
        self.assertEqual(record.state, Record.USED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'status': 'success',
            'message': 'all correct',
        })

    def test_report_success(self):
        pass
