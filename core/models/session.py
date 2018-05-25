from core.validators import student_id_validator
from django.db import models

class Session(models.Model):
    """
    Represents a vote session.
    """

    CREATED = '0'
    AUTHENTICATED = '1'
    AUTHORIZED = '2'
    VOTING = '3'
    VOTED = '9'

    NOT_AUTHENTICATED = 'X'
    NOT_VERIFIED = 'Y'
    CANCELED = 'Z'
    ABORTED = 'Q'
    BANNED = 'N'

    STATE_CHOICES = (
        (CREATED, 'Created'),
        (AUTHENTICATED, 'Authenticated'),
        (AUTHORIZED, 'Authorized'),
        (VOTING, 'Voting'),
        (VOTED, 'Voted'),
        (NOT_AUTHENTICATED, 'Not authenticated'),
        (NOT_VERIFIED, 'Not verified'),
        (CANCELED, 'Canceled'),
        (ABORTED, 'Aborted'),
        (BANNED, 'Banned'),
    )

    station = models.ForeignKey('Station', on_delete=models.PROTECT, null=True, related_name='sessions')
    student_id = models.CharField(max_length=9, db_index=True, validators=[student_id_validator])
    revision = models.IntegerField(default=0)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=CREATED)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '[{state}] {name}'.format(**self.__dict__)
