from django.db import models
from rest_framework.authtoken.models import Token as BaseToken

# NOTE: be careful of this bug: <https://github.com/encode/django-rest-framework/issues/705>,
# add `'rest_framework.authtoken'` to `INSTALLED_APPS` if necessary.

class Token(BaseToken):
    """
    Represents an authorization token.
    """
    is_expired = models.BooleanField(default=False)
