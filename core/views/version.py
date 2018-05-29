import os
import re
from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

class VersionView(APIView):
    """
    Returns the running instance version if available.
    """

    def get(self, request):
        try:
            # Reads Git HEAD file and parse its ref
            with open(os.path.join(settings.BASE_DIR, '.git/HEAD'), 'r') as f:
                buf = f.read().strip()

            # Make sure the HEAD file is something we expect
            head = re.match(r'^ref:\s*(refs/heads/[A-Za-z0-9\-_]+)$', buf).group(1)

            # Reads the ref commit hash
            with open(os.path.join(settings.BASE_DIR, '.git', head), 'r') as f:
                ref = f.read().strip()

            # Returns the running commit version
            return Response({ 'ref': ref })

        except (FileNotFoundError, AttributeError):
            # Either the instance is not deployed using Git, or HEAD is not in
            # known state.
            raise NotFound
