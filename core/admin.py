from django.contrib import admin
from .models import Entry, OverrideEntry

admin.site.register(Entry)
admin.site.register(OverrideEntry)
