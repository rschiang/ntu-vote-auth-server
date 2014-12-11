from .models import AuthCode, VoteEntry

def do_import(filename):
    '''
    Imports auth code from single plain text file.
    '''
    with open(filename, 'r') as f:
        codes = []
        for line in f:
            if not line:
                continue

            code = AuthCode()
            code.kind = line[:2]
            code.code = line.strip()
            codes.append(code)

        AuthCode.objects.bulk_create(codes)

def get_student(student_id):
    return VoteEntry.objects.filter(student_id__startswith=student_id)
