from account.models import User
from rest_framework.permissions import BasePermission

class IsStationStaff(BasePermission):
    """
    Allow access only to station staff accounts.
    """

    def has_permission(self, request, view):
        return request.user and request.user.kind == User.STATION
