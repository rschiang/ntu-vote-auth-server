import hashlib

from django.utils.crypto import get_random_string
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class Record(models.Model):

    UNAVAILABLE = 'U'
    AVAILABLE = 'A'
    LOCKED = 'L'
    VOTING = 'V'
    USED = 'U'
    FLAGGED = 'F'
    RESETTING = 'R'

    STATE_CHOICES = (
        (UNAVAILABLE, 'Unavailable'),
        (AVAILABLE, 'Available'),
        (LOCKED, 'Locked'),
        (VOTING, 'Voting'),
        (USED, 'Used'),
        (FLAGGED, 'Flagged'),
        (RESETTING, 'Resetting')
    )

    student_id = models.CharField(max_length=10, unique=True)
    revision = models.IntegerField(default=0)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=AVAILABLE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{student_id} [{state}]'.format(**self.__dict__)


class AuthCode(models.Model):
    """
    ballot, using a valid AuthToken to exchange this one
    """
    kind = models.CharField(max_length=2)
    code = models.CharField(max_length=256)
    issued = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class AuthToken(models.Model):
    """
    Token for authentication
    """
    student_id = models.CharField(max_length=10)
    station_id = models.IntegerField()
    kind = models.CharField(max_length=2)
    code = models.CharField(max_length=256, unique=True)
    confirm_code = models.CharField(max_length=256, unique=True)
    issued = models.BooleanField(default=False)
    timestamp = models.DateTimeField()

    def __str__(self):
        return '{timestamp}'.format(**self.__dict__)

    @classmethod
    def generate(cls, student_id, station_id, kind):
        t = timezone.now()
        s = '&'.join((student_id, station_id, kind, t.isoformat(), settings.SECRET_KEY))
        h = hashlib.sha256(s.encode()).hexdigest().upper()

        token = AuthToken(student_id=student_id, station_id=station_id, kind=kind)
        token.code = h
        token.timestamp = t
        token.confirm_code = get_random_string(16)
        return token


class Entry(models.Model):
    dpt_code = models.CharField(max_length=4, unique=True)
    kind = models.CharField(max_length=5, null=True)
    name = models.CharField(max_length=256, null=True)

    def __str__(self):
        return "{s.dpt_code}-{s.kind}-{s.name}".format(s=self)


class OverrideEntry(models.Model):
    student_id = models.CharField(max_length=10, unique=True,
            validators=[RegexValidator(regex=r'[A-Z]\d{2}[0-9A-Z]\d{5}'),])
    entry = models.ForeignKey('Entry', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "{s.student_id} ({s.entry})".format(s=self)
