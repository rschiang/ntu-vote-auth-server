from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Represents an election staff.
    """

    ADMIN = 'A'
    STATION = 'S'
    SUPERVISOR = 'V'
    REMOTE_SERVER = 'R'

    KIND_CHOICES = (
        (ADMIN, 'Administrator'),
        (STATION, 'Station staff'),
        (SUPERVISOR, 'Supervisor'),
        (REMOTE_SERVER, 'Remote server'),
    )

    kind = models.CharField(max_length=1, choices=KIND_CHOICES)

    def __str__(self):
        return self.username
