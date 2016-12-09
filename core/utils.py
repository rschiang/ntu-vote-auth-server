import logging
from hashlib import md5
from string import ascii_uppercase as UPPERCASE
from django.utils.crypto import get_random_string
from django.db import transaction
from .models import AuthCode, AuthToken, Record, Entry
from core import meta

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

def setup_entry():
    for key in meta.DPTCODE_NAME:
        entry, _ = Entry.objects.get_or_create(dpt_code=key)
        entry.name = meta.DPTCODE_NAME[key]
        entry.save()

def generate_auth_code(kind=None, amount=1000):
    """
    Generate auth code
    """
    if kind is None:
        kind = '$$'
    code = [kind, '', '', '']
    with transaction.atomic():
        for i in range(amount):
            code[1] = get_random_string(length=9, allowed_chars=UPPERCASE)
            code[2] = get_random_string(length=9, allowed_chars=UPPERCASE)
            code[3] = code[1] + md5(code[2].encode()).hexdigest()
            code[3] = md5(code[3].encode()).hexdigest()[:5].upper()
            auth_code = AuthCode()
            auth_code.kind = kind
            auth_code.code = '-'.join(code)
            auth_code.save()

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
        record = Record.objects.get_or_create(student_id=student_id)
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
