from django.core.validators import RegexValidator

student_id_validator = RegexValidator(regex=r'[A-Z]\d{2}[0-9A-Z]\d{5}')

def validate_student_id(value):
    return student_id_validator(value)
