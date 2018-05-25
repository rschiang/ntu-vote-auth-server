from account.models import User
from rest_framework.permissions import BasePermission

class IsStationStaff(BasePermission):
    """
    Only allows access from station staff accounts.
    """

    def has_permission(self, request, view):
        return request.user and request.user.kind == User.STATION


class IsRemoteServer(BasePermission):
    """
    Only allows access from remote server accounts, usually for callbacks.
    """

    def has_permission(self, request, view):
        # TODO: Check HOST
        return request.user and request.user.kind == User.REMOTE_SERVER
