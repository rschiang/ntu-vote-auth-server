import os
from core.models import Session, Election
from core.services import aca, vote, AuthenticationError
from core.views.helpers import query_ballots
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Issue remote voting auth code elector'

    def add_arguments(self, parser):
        parser.add_argument('student_id', nargs='+', type=str)

    def handle(self, *args, **options):
        election = Election.objects.get()
        for student_id in options['student_id']:
            revision = 0
            try:
                ballots = query_ballots(student_id, revision)
            except AuthenticationError as e:
                try:
                    revision = int(e.detail[-1:])
                    ballots = query_ballots(student_id, revision)
                except:
                    print('Failed to query revision', student_id)
                    continue

            session = Session.objects.create(election=election, student_id=student_id, revision=revision, state=Session.BANNED)
            session.ballots.add(*ballots)

            ballot_ids = sorted(ballot.foreign_id for ballot in ballots)
            auth_code = vote.request_auth_code(ballot_ids)

            session.auth_code = auth_code
            session.save()
            print('Issued', auth_code, 'for', student_id, 'kind', ballot_ids)
