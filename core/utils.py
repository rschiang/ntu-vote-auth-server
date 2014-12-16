import re
from .models import AuthCode, Record, CooperativeMember

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

def import_coop_member(filename=None):
    '''
    Imports coop member entries from CSV file.
    '''
    with open(filename or 'coop.csv', 'r') as f:
        members = {}
        for line in f:
            serial, _, student_id = line.partition(',')
            serial = serial.strip()
            student_id = student_id.strip().upper()

            if not (serial and re.match(r'[A-Z]\d{2}[0-9AB]\d{5}', student_id)):
                print('Invalid line:', line)
                continue
            elif student_id in members:
                member = members[student_id]
                print('Duplicate entry:', member.serial, member.student_id)

            member = CooperativeMember()
            member.serial = serial
            member.student_id = student_id
            members[student_id] = member

        CooperativeMember.objects.bulk_create(members.values())

def reset_server_state():
    auth_codes = AuthCode.objects.filter(issued=True)
    records = Record.objects.all()
    print('Issued auth codes:', auth_codes.count())
    print('Record entries:', records.count())

    row_count = auth_codes.update(issued=False)
    print('... reset %s rows.', row_count)

    records.delete()
    print('... cleared.')

def wipe_auth_code():
    AuthCode.objects.all().delete()

def wipe_coop_member():
    CooperativeMember.objects.all().delete()

def get_student(student_id):
    return Record.objects.get(student_id=student_id)
