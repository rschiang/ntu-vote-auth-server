from core.models import Session
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime

SESSION_STATES = {
    Session.CREATED: 'CREATED',
    Session.AUTHENTICATED: 'AUTH-S1',
    Session.AUTHORIZED: 'AUTH-S2',
    Session.VOTING: 'VOTING',
    Session.VOTED: 'VOTED',
    Session.NOT_AUTHENTICATED: 'NONAUTH',
    Session.NOT_VERIFIED: 'REJECTED',
    Session.CANCELED: 'CANCELD',
    Session.ABORTED: 'ABORTED',
    Session.BANNED: 'BANNED',
}

class Command(BaseCommand):
    help = 'Query elector status'

    def add_arguments(self, parser):
        parser.add_argument('student_id', nargs='+', type=str)

    def handle(self, *args, **options):
        for student_id in options['student_id']:
            sessions = Session.objects.filter(student_id=student_id).order_by('created')
            if not sessions:
                print('No record found for student', student_id)
            else:
                print('Sessions for student', student_id)
                for session in sessions:
                    print('{} [{}] {}-{} {}'.format(localtime(session.created), SESSION_STATES[session.state].ljust('7'),
                                                    session.student_id, session.revision, session.auth_code or '<no code>'))
                print('=' * 40)
