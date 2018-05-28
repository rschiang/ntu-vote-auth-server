from core.models import Election
from django.conf import settings
from rest_framework.permissions import BasePermission

class IsElectionRunning(BasePermission):
    """
    Only allows access when current election is running and the station is associated with the election.
    """

    def has_object_permission(self, request, view, obj):
        return obj.state == Election.STARTED

class IsAssociatedElection(BasePermission):
    """
    Only allows access when the current station is associated with the election.
    """

    def has_object_permission(self, request, view, obj):
        try:
            return request.user.station.election == obj
        except AttributeError:
            return False        # No station or election associated

class IsFromVoteSystem(BasePermission):
    """
    Only allows access from vote system if configured with `VOTE_HOST`.
    """

    def has_permission(self, request, view):
        if settings.VOTE_HOST:
            host = request.META['REMOTE_HOST']
            addr = request.META['REMOTE_ADDR']
            return (host == settings.VOTE_HOST or addr == settings.VOTE_HOST)
        return True     # No host configured
