import time
from django.core import mail

def send_auth_codes(subject, template, receivers, **kwargs):
    count = 0
    with mail.get_connection():
        for student_id, auth_code in receivers.items():
            count += 1
            body = template.format(student_id=student_id, auth_code=auth_code)
            from_email = kwargs.get('from_email')
            to_email = student_id.lower() + '@ntu.edu.tw'
            reply_to = kwargs.get('reply_to', 'vote@ntustudents.org')

            message = mail.EmailMessage(subject=subject, body=body, from_email=from_email, to=[to_email], reply_to=[reply_to])
            message.send()

            print('#{} {} sent\n'.format(count, student_id))
            time.sleep(1)
