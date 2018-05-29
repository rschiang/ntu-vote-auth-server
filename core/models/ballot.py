from django.core.exceptions import ObjectDoesNotExist
from django.db import models

class BallotManager(models.Manager):
    """
    Custom manager to populate eligibility conditions early.
    """

    def all_ballots(self, election=None):
        """
        Returns all ballots with their expressions prefetched.
        """
        queryset = self.filter(election=election) if election else self
        return queryset.prefetch_related('conditions').all()


class Ballot(models.Model):
    """
    Represents individual elections in an election event, with specific set of
    candidates and elector requirements. This is known as a type of ballot (“票種”)
    to users.
    """

    # Use custom manager to load expressions
    objects = BallotManager()

    # The election associated with this ballot
    election = models.ForeignKey('Election', on_delete=models.CASCADE)

    # Ballot ID in vote system
    foreign_id = models.IntegerField()

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def condition(self):
        """
        Returns the root condition, or None if there aren't any.
        """
        try:
            return self.conditions.get(parent=None)
        except ObjectDoesNotExist:
            return None

    def match(self, fields):
        """
        Returns if the given fields match the conditions of this ballot.
        """
        condition = self.condition
        if condition:
            return condition.match(fields, queryset=self.conditions.all())
        return True     # If no condition given, default to True.
