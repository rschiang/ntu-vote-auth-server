from .models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class AccountTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate(self, request):
        user, token = super().authenticate(request)
        if token.is_expired:
            raise AuthenticationFailed('Token expired.')
        # TODO: Insert telemetry here
        return user, token
