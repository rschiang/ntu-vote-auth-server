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
        members = []
        for line in f:
            serial, _, student_id = line.partition(',')
            if not serial or not student_id:
                print('Invalid line:', line)
                continue

            member = CooperativeMember()
            member.serial = serial
            member.student_id = student_id
            members.append(member)

        CooperativeMember.objects.bulk_create(members)

def get_student(student_id):
    return Record.objects.get(student_id=student_id)
