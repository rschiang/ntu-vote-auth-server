from django.db import models
from .validators import student_id_validator

class AuthCode(models.Model):
    """
    Represents an authorized voting auth code.
    """

    # The election associated with this condition
    election = models.ForeignKey('Election', on_delete=models.CASCADE, related_name='auth_codes')

    student_id = models.CharField(max_length=9, unique=True, validators=[student_id_validator])
    code = models.CharField(max_length=256)

    def __str__(self):
        return '[{election}] {student_id}: {code}'.format(**self.__dict__)
