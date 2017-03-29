import logging

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from .models import Entry, OverrideEntry, Record

logger = logging.getLogger('admin')


class EntryAdmin(admin.ModelAdmin):
    list_display = ('dpt_code', 'kind', 'name')
    ordering = ('dpt_code',)
    search_fields = ('name',)


class OverrideEntryAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'entry')
    ordering = ('student_id',)
    search_fields = ('student_id',)


class RecordAdmin(admin.ModelAdmin):
    readonly_fields = ('student_id', 'revision', 'state')
    actions = ('unlock', 'apply_blacklist')
    list_filter = ('state',)
    search_fields = ('student_id',)

    def unlock(self, request, records):
        """
        Unlock selected students which must be lock state.
        """
        records.update(state=Record.AVAILABLE)
        for record in records:
            admin.models.LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get(models='Record').id,
                object_id=record.pk,
                object_repr=force_unicode(record),
                action_flag=admin.models.CHANGE,
                change_message='Record was unlocked by {}'.format(request.user.username),
            )
            logger.info('Record [%s] was set to available (was #%s)', record.student_id, record.pk)

    def apply_blacklist(self, request, records):
        """
        Apply some student to black list.
        """
        for record in records:
            record.state = Record.UNAVAILABLE
            record.save()
            admin.models.LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get(models='Record').id,
                object_id=record.pk,
                object_repr=force_unicode(record),
                action_flag=admin.models.CHANGE,
                change_message='Record was locked by {}'.format(request.user.username),
            )
            logger.info('Record [{record}] was blacklisted.'.format(
                record=record.student_id
            ))

    def get_actions(self, request):
        """
        disable default action 'delete_selected'
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(OverrideEntry, OverrideEntryAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Record, RecordAdmin)
