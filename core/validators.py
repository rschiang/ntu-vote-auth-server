from django.core.validators import RegexValidator

internal_id_validator = RegexValidator(regex=r'[0-9a-f]{8}')
student_id_validator = RegexValidator(regex=r'[A-Z]\d{2}[0-9A-Z]\d{5}')

def validate_student_id(value):
    return student_id_validator(value)
