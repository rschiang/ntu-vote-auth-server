from core.service import BaseEntryRule
from core.service import entry_provider
from core.models import Entry, OverrideEntry


class NormalEntryRule(BaseEntryRule):
    queryset = Entry.objects.all()
    lookup_field = 'dpt_code'
    lookup_info_kwarg = 'department'
    entry_field = 'kind'


class OverrideEntryRule(BaseEntryRule):
    queryset = OverrideEntry.objects.all()

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
