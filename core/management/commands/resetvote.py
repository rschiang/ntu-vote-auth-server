import os
from core.models import Session
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Reset vote server'

    def handle(self, *args, **options):
        Session.objects.exclude(state=Session.BANNED).delete()
        logging_dir = settings.LOGGING_DIR
        for f in os.listdir(logging_dir):
            os.truncate(os.path.join(logging_dir, f))
