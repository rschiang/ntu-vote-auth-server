from django.db import models

class VoteEntry(models.Model):
    student_id = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

class AuthCode(models.Model):
    kind = models.CharField(max_length=2)
    code = models.CharField(max_length=256)
    issued = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
