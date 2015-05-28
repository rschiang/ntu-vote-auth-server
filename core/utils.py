import logging
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

def apply_blacklist(*student_ids):
    count = 0
    for student_id in student_ids:
        record, _ = Record.objects.get_or_create(student_id=student_id)
        if record.state == Record.AVAILABLE:
            record.state = Record.UNAVAILABLE
            record.save()
        else:
            print('SKIPPED: [{}] bears another state ʻ{}ʻ'.format(student_id, record.state))
            continue
        count += 1
    print('... blacklisted {} IDs.'.format(count))

def unlock_student(student_id, force=False):
    logger = logging.getLogger('vote')
    logger.info('Unlocking requested for student %s', student_id)

    try:
        record = Record.objects.get(student_id=student_id)
    except Record.DoesNotExist:
        print('Student is not locked.')
        return False

    if not (record.state == Record.LOCKED or force):
        print('Student is not in lock state (%s). Use force to clear anyway.', record.state)
        return False

    record.delete()
    if force:
        logger.info('Record [%s] was forcibly deleted (was #%s, state ʻ%sʻ)', record.student_id, record.id, record.state)
    else:
        logger.info('Record [%s] deleted (was #%s)', record.student_id, record.id)
    return True

def extract_code(kind):
    logger = logging.getLogger('vote')
    codes = AuthCode.objects.filter(issued=False, kind=kind).order_by('-id')
    for i in codes:
        if not i.issued:
            i.issued = True
            i.save()

            logger.info('Extract token %s manually', i.code)
            print(i.code)
            break
