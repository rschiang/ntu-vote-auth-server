from django.apps import AppConfig

from core.service import kind_classifier


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from . import entry
        # kind_classifier will retun the first not None value, in other words
        # the later rule may be ignore.
        kind_classifier.register('override', entry.OverrideEntryRule)
        kind_classifier.register('coss', entry.COSSEntryRule)
        kind_classifier.register('medicine', entry.MedicineEntryRule)
        kind_classifier.register('normal undergraduate', entry.UndergraduateEntryRule)
        kind_classifier.register('normal graduate', entry.GraduateEntryRule)
