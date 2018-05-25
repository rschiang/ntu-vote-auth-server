from account.permissions import IsRemoteServer, IsStationStaff
from core.models import Election
from core.permissions import IsAssociatedElection, IsElectionRunning
from rest_framework.generics import GenericAPIView

class BaseElectionView(GenericAPIView):
    """
    Base class for election-specific API views.
    """
    permission_classes = (IsStationStaff, IsAssociatedElection, IsElectionRunning)

    queryset = Election.objects.all()
    lookup_url_kwarg = 'name'


class BaseElectionEventView(BaseElectionView):
    """
    Base class for remote server callback event views.
    """
    permission_classes = (IsRemoteServer,)
