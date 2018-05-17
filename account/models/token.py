import base64
import os
from django.db import models

def generate_token_key():
    return base64.b32encode(os.urandom(25)).decode()

class Token(models.Model):
    """
    An authorization token.
    """
    key = models.CharField(max_length=40, primary_key=True, default=generate_token_key)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tokens')
    created = models.DateTimeField(auto_now_add=True)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.key
