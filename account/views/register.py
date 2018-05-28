import logging
from account.models import Token
from account.throttling import StrictAnonRateThrottle
from django.db import transaction
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

logger = logging.getLogger('vote.auth')

class RegisterView(ObtainAuthToken):
    throttle_classes = (StrictAnonRateThrottle,)

    def post(self, request, *args, **kwargs):
        # Authenticate user by default serializer
        serializer = self.serializer_class(data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            logger.error('Login attempt failed')
            logger.info(serializer.initial_data)
            raise

        user = serializer.validated_data['user']

        # Invalidate any previous token
        with transaction.atomic():
            old_token_count = Token.objects.filter(user=user).update(is_expired=True)
            token = Token.objects.create(user=user)

        logger.info('User %s logged in, %s old tokens expired', user.username, old_token_count)

        return Response({
            'status': 'success',
            'token': token.key,
        })
