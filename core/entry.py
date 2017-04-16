from core.service import BaseEntryRule
from core.service import kind_classifier
from core.models import Entry, OverrideEntry

import logging
logger = logging.getLogger('vote.service')


class NormalEntryRule(BaseEntryRule):
    queryset = Entry.objects.all()
    lookup_field = 'dpt_code'
    lookup_info_kwarg = 'department'
    entry_field = 'kind'


class OverrideEntryRule(BaseEntryRule):
    queryset = OverrideEntry.objects.all()
    lookup_field = 'student_id'
    lookup_info_kwarg = 'id'
    entry_field = 'entry'

    def get_kind(self, student_info):
        try:
            return super().get_kind(student_info).kind
        except:
            return None


# The order is importent
kind_classifier.register('override', OverrideEntryRule)

# put department specific rule here

kind_classifier.register('normal', NormalEntryRule)
