import base64
import os
from core.validators import student_id_validator
from django.db import models

def generate_session_key():
    return base64.b32encode(os.urandom(5)).decode()

class Session(models.Model):
    """
    Represents a vote session.
    """

    CREATED = '0'
    AUTHENTICATED = '1'
    AUTHORIZED = '2'
    VOTING = '3'
    VOTED = '9'

    NOT_AUTHENTICATED = 'X'     # Elector wasn't authenticated by canonical source.
    NOT_VERIFIED = 'Y'  # Elector didn't confirm their idenitity.
    CANCELED = 'Z'  # Elector left before being allocated a booth.
    ABORTED = 'Q'   # Elector left the booth before finishing their vote.
    BANNED = 'N'    # Fake session to ban a user permanently in an election.

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

    election = models.ForeignKey('Election', on_delete=models.CASCADE, related_name='sessions')
    station = models.ForeignKey('Station', on_delete=models.SET_NULL, null=True, related_name='sessions')
    student_id = models.CharField(max_length=9, db_index=True, validators=[student_id_validator])
    revision = models.IntegerField(default=0)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=CREATED)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Session-specific information
    auth_code = models.CharField(max_length=256, blank=True)
    ballots = models.ManyToManyField('Ballot')      # Ballots matched during authentication
    key = models.CharField(max_length=8, default=generate_session_key)  # Unique session key

    def __str__(self):
        return '[{state}] S{station_id} {student_id}[{revision}]'.format(**self.__dict__)

    def save_state(self, state):
        """
        Sets and saves the session state.
        """
        self.state = state
        self.save()
