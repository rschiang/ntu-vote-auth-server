from account.models import User, Station, Session
from core.models import Record, AuthToken, AuthCode, Entry
from core import service, meta

from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import override_settings


class CoreTestCase(APITestCase):

    fixtures = ['fixtures/entry.json']

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
            session = Session.objects.get(user=self.user)
        except:
            session = None
        self.session = session
        self.token = session.token

        self.authcode = AuthCode(kind='70', code='70-ZU2U0RAKX-KOXLUYHJI-7C05B')
        self.authcode.save()

    def test_entry_loaded(self):
        self.assertEqual(Entry.objects.count(), 216)

    @override_settings(
        ACA_API_URL='http://localhost:3000/seqServices/stuinfoByCardno',
        ACA_API_USER='aca_api_user', ACA_API_PASSWORD='password',
        ENFORCE_CARD_VALIDATION=True)
    def test_authenticate_success(self):
        entry, _ = Entry.objects.get_or_create(dpt_code='1010')
        entry.kind = 'A0'
        entry.save()
        cid = '12345678'
        aca_info = service.to_student_id(cid)
        uid = aca_info.id
        uid = uid + '0'
        url = reverse('authenticate')
        data = {'cid': cid, 'uid': uid,
                'token': self.token,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = AuthToken.objects.get(student_id=aca_info.id)
        self.assertEqual(response.data, {
            'vote_token': token.code,
            'uid': aca_info.id,
            'type': aca_info.college,
            'college': meta.DPTCODE_NAME[aca_info.department],
            'status': 'success'
        })

    def test_confirm_success(self):
        record = Record(student_id=self.student_id)
        record.state = Record.LOCKED
        record.save()
        vote_token = AuthToken.generate(self.student_id, str(self.station.external_id), '70')
        vote_token.save()

        url = reverse('confirm')
        data = {'uid': self.student_id,
                'vote_token': vote_token.code, 'token': self.token,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        response = self.client.post(url, data)
        callback = 'https://{0}{1}?callback={2}'.format(
            settings.CALLBACK_DOMAIN, reverse('callback'), vote_token.confirm_code)
        self.assertEqual(response.data, {
            'status': 'success',
            'ballot': self.authcode.code,
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
        record = Record(student_id=self.student_id)
        record.state = Record.LOCKED
        record.save()
        vote_token = AuthToken.generate(self.student_id, str(self.station.external_id), '70')
        vote_token.save()

        url = reverse('report')
        data = {
            'uid': self.student_id,
            'vote_token': vote_token.code,
            'token': self.token,
            'api_key': settings.API_KEY, 'version': settings.API_VERSION,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.data, {'status': 'success'})

    def test_status(self):
        username = 'admin'
        password = 'station1'
        user = User(username=username)
        user.set_password(password)
        user.kind = User.ADMIN
        user.save()

        # login
        data = {'username': username, 'password': password,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION}
        client = APIClient()
        client.post(reverse('register'), data, format='json')

        try:
            session = Session.objects.get(user=user)
        except:
            session = None
        else:
            url = '/api/status'
            data = {
                'token': session.token,
                'api_key': settings.API_KEY, 'version': settings.API_VERSION,
            }
            response = self.client.post(url, data)


class ACATestCase(APITestCase):
    @override_settings(
        ACA_API_URL='http://localhost:3000/seqServices/stuinfoByCardno',
        ACA_API_USER='aca_api_user', ACA_API_PASSWORD='password')
    def test_get_student_info(self):
            service.to_student_id('123456')
