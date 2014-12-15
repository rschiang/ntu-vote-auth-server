from django.db import models

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
