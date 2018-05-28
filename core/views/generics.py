from account.permissions import IsRemoteServer, IsStationStaff
from core.models import Election
from core.permissions import IsAssociatedElection, IsElectionRunning, IsFromVoteSystem
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
    # Note that we don't enforce election state checking, since the callback
    # could be arriving much later. This should not be an issue now, but we'll
    # just document the whole thing.
    permission_classes = (IsRemoteServer, IsFromVoteSystem)
