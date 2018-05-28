from .models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class AccountTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate(self, request):
        auth = super().authenticate(request)
        if len(auth) > 1:
            user, token = auth
            if token.is_expired:
                raise AuthenticationFailed('Token expired.')
            # TODO: Insert telemetry here
        return auth
