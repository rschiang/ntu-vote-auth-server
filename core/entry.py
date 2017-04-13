from core.service import BaseEntryRule
from core.service import entry_provider
from core.models import Entry, OverrideEntry


class NormalEntryRule(BaseEntryRule):
    queryset = Entry.objects.all()
    lookup_field = 'dpt_code'
    entry_field = 'kind'

    def get_object(self, student_info):
        try:
            entry = self.get_queryset().get(dpt_code=student_info.department)
            return entry.kind
        except Entry.DoesNotExist:
            return None


class OverrideEntryRule(BaseEntryRule):
    queryset = OverrideEntry.objects.all()
    lookup_field = 'student_id'
    entry_field = 'entry.kind'

    def get_object(self, student_info):
        try:
            override_entry = self.get_queryset().get(student_id=student_info.id)
            return override_entry.entry.kind
        except OverrideEntry.DoesNotExist:
            return None


# The order is importent
entry_provider.register('override', OverrideEntryRule)

# put department specific rule here

entry_provider.register('normal', NormalEntryRule)
