from django.db import models
from django.utils import timezone
from .errors import InvalidState

class Election(models.Model):
    """
    Represents an election event.
    """

    NOT_STARTED = '-'
    STARTED = '>'
    PAUSED = '|'
    ENDED = '='

    STATE_CHOICES = (
        (NOT_STARTED, 'Not started'),
        (STARTED, 'Started'),
        (PAUSED, 'Paused'),
        (ENDED, 'Ended'),
    )

    name = models.SlugField(max_length=16, unique=True)
    description = models.TextField(blank=True)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=NOT_STARTED)
    start_time = models.DateTimeField(null=True, default=None)
    end_time = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return '[{state}] {name}'.format(**self.__dict__)

    def start(self):
        """
        Starts or resumes the election.
        """
        if self.state == Election.NOT_STARTED:
            self.start_time = timezone.now()
        elif self.state != Election.PAUSED:
            raise InvalidState('Expect PAUSED', value=self.state)
        self.state = Election.STARTED
        self.save()

    def pause(self):
        """
        Pauses the election.
        """
        if self.state != Election.STARTED:
            raise InvalidState('Expect STARTED', value=self.state)
        self.state = Election.PAUSED
        self.save()

    def end(self):
        """
        Ends the election.
        """
        self.end_time = timezone.now()
        self.state = Election.ENDED
        self.save()
