from django.apps import AppConfig

from core.service import kind_classifier


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from . import entry
        kind_classifier.register('override', entry.OverrideEntryRule)

        kind_classifier.register('normal', entry.NormalEntryRule)
