from core.services import aca
from core.models import Ballot, Elector, Election
from django.conf import settings

def query_ballots(student_id, revision):
    election = Election.objects.get()
    info = aca.query_student(student_id + str(revision))

    # Build up elector information for condition matching
    student_type = info.id[0]
    elector_data = {
        # Known information
        'type': student_type, 'college': info.college_id, 'department': info.department,
        # Normalized information
        'standing': ('R' if student_type in settings.GRADUATE_CODE else
                     ('B' if student_type in settings.UNDERGRADUATE_CODE else '')),
    }

    # Filter out ineligible identities as regulated in Election & Recall Act §13(2).
    if student_type not in settings.GENERAL_CODE:
        return None

    # Iterate through ballots and check eligibility
    ballots = []
    for ballot in Ballot.objects.all_ballots(election=election):
        # 1) Check if the elector is explicitly specified in list.
        # Takes presedence over all ballot conditions.
        try:
            elector = ballot.electors.get(student_id=student_id)
            if elector.is_allowed:
                ballots.append(ballot)
            continue
        except Elector.DoesNotExist:
            pass    # This elector isn't explicitly black/whitelisted. Good.

        # 2) Matches the elector data against ballot conditions.
        # We've done the logic on models, so just call the method.
        if ballot.match(fields=elector_data):
            ballots.append(ballot)

    # 3) Checks if there is at least one ballot to vote.
    return ballots or None
