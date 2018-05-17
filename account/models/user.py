from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Choices
    ADMIN = 'A'
    STATION = 'S'
    SUPERVISOR = 'V'

    KIND_CHOICES = (
        (ADMIN, 'Administrator'),
        (STATION, 'Station staff'),
        (SUPERVISOR, 'Supervisor'),
    )

    kind = models.CharField(max_length=1, choices=KIND_CHOICES)

    def __str__(self):
        return self.username
