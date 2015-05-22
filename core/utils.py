import re
from .models import AuthCode, AuthToken, Record

def import_auth_code(filename=None):
    '''
    Imports auth code from single plain text file.
    '''
    with open(filename or 'authcode.csv', 'r') as f:
        codes = []
        for line in f:
            if not line:
                continue

            code = AuthCode()
            code.kind = line[:2]
            code.code = line.strip()
            codes.append(code)

        AuthCode.objects.bulk_create(codes)

def reset_server_state():
    auth_codes = AuthCode.objects.filter(issued=True)
    tokens = AuthToken.objects.all()
    records = Record.objects.all()
    print('Issued auth codes:', auth_codes.count())
    print('Generated tokens:', tokens.count())
    print('Record entries:', records.count())

    row_count = auth_codes.update(issued=False)
    print('... reset %s rows.' % row_count)

    tokens.delete()
    records.delete()
    print('... cleared.')

def wipe_auth_code():
    AuthCode.objects.all().delete()

def get_student(student_id):
    return Record.objects.get(student_id=student_id)
