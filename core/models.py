from django.db import models

class VoteEntry(models.Model):
    internal_id = models.CharField(max_length=32)
    student_id = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

class AuthCode(models.Model):
    code = models.CharField(max_length=256)
    issued = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)