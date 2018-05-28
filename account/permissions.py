from account.models import User
from django.conf import settings
from rest_framework.permissions import BasePermission

class IsStationStaff(BasePermission):
    """
    Only allows access from station staff accounts.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.kind == User.STATION


class IsRemoteServer(BasePermission):
    """
    Only allows access from remote server accounts, usually for callbacks.
    """

    def has_permission(self, request, view):
        host_allowed = True
        if settings.VOTE_HOST:  # Check hostname if it was specified
            host = request.META.get('REMOTE_HOST')
            addr = request.META.get('REMOTE_ADDR')
            # TODO: Log hostname if not matched
            host_allowed = (host == settings.VOTE_HOST or addr == settings.VOTE_HOST)

        return request.user.is_authenticated and request.user.kind == User.REMOTE_SERVER and host_allowed
