from .validators import internal_id_validator, student_id_validator, session_key_validator
from django.conf import settings
from rest_framework import serializers

class AuthenticateSerializer(serializers.Serializer):
    """
    Represents an authenticate request.
    """
    internal_id = serializers.CharField(validators=[internal_id_validator], allow_blank=True)
    student_id = serializers.CharField(validators=[student_id_validator], allow_blank=True)
    revision = serializers.IntegerField(min_value=0)

    def validate_internal_id(self, value):
        if not settings.CARD_VALIDATION_OFF and not value:
            raise serializers.ValidationError('Internal ID could not be blank with current validation mode')
        return value

    def validate_student_id(self, value):
        if not settings.CARD_VALIDATION_QUIRK and not value:
            raise serializers.ValidationError('Student ID could not be blank with current validation mode')
        return value

class VerifySerializer(serializers.Serializer):
    """
    Represents a general verification request, either confirmation or rejection.
    """
    student_id = serializers.CharField(validators=[student_id_validator])
    session_key = serializers.CharField(validators=[session_key_validator])

class VoteEventSerializer(serializers.Serializer):
    """
    Represents a general event callback from vote system.
    """
    auth_code = serializers.CharField(max_length=256)
