import logging

from django.contrib import admin, messages
from .models import Entry, OverrideEntry, AuthCode, Record
from . import utils

admin.site.register(Entry)
admin.site.register(OverrideEntry)

logger = logging.getLogger('admin')

class RecordAdmin(admin.ModelAdmin):
    readonly_fields = ('student_id', 'revision', 'state')
    actions = ('unlock', 'apply_blacklist')
    list_filter = ('state',)

    def unlock(self, request, records):
        for record in records:
            if record.state == Record.LOCKED:
                record.delete()
                logger.info('Record [%s] deleted (was #%s)', record.student_id, record.pk)
            else:
                self.message_user(request, "Student [{}] is not in lock state.".format(record.student_id), level=messages.ERROR)

    def apply_blacklist(self, request, records):
        for record in records:
            record.state = Record.UNAVAILABLE
            record.save()
            logger.info('Record [{record}] was blacklisted.'.format(
                record=record.student_id
                )
            )


admin.site.register(Record, RecordAdmin)
