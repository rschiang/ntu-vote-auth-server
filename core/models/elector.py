from core.validators import student_id_validator
from django.db import models

class Elector(models.Model):
    """
    Represents a qualified or blacklisted elector for a single ballot.
    """

    # The ballot associated with this condition
    ballot = models.ForeignKey('Ballot', on_delete=models.CASCADE, related_name='electors')

    student_id = models.CharField(max_length=9, validators=[student_id_validator])
    is_allowed = models.BooleanField(default=True)

    def __str__(self):
        return '[{}] {}'.format('✅' if self.is_allowed else '⛔', self.student_id)
