from core.models import Election
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
