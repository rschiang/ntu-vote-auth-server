import hashlib
from django.conf import settings
from django.db import models
from django.utils import timezone

class CooperativeMember(models.Model):
    student_id = models.CharField(max_length=10, unique=True)
    serial = models.CharField(max_length=16, unique=True)

class Record(models.Model):
    UNAVAILABLE = 'U'
    AVAILABLE = 'A'
    LOCKED = 'L'
    USED = 'U'
    FLAGGED = 'F'

    STATE_CHOICES = (
        (UNAVAILABLE, 'Unavailable'),
        (AVAILABLE, 'Available'),
        (LOCKED, 'Locked'),
        (USED, 'Used'),
        (FLAGGED, 'Flagged'),
    )

    student_id = models.CharField(max_length=10, unique=True)
    revision = models.IntegerField(default=0)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=AVAILABLE)
    timestamp = models.DateTimeField(auto_now=True)

class AuthCode(models.Model):
    kind = models.CharField(max_length=2)
    code = models.CharField(max_length=256)
    issued = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class AuthToken(models.Model):
    student_id = models.CharField(max_length=10)
    station_id = models.IntegerField()
    kind = models.CharField(max_length=2)
    code = models.CharField(max_length=256, unique=True)
    issued = models.BooleanField(default=False)
    timestamp = models.DateTimeField()

    @classmethod
    def generate(cls, student_id, station_id, kind):
        t = timezone.now()
        s = '&'.join((student_id, station_id, kind, t.isoformat(), settings.SECRET_KEY))
        h = hashlib.sha256(s.encode()).hexdigest().upper()

        token = AuthToken(student_id=student_id, station_id=station_id, kind=kind)
        token.code = h
        token.timestamp = t
        return token
