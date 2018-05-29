import logging
from account.models import User
from account.permissions import IsRemoteServer, IsStationStaff
from core.models import Election
from core.permissions import IsAssociatedElection, IsElectionRunning
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import ValidationError

logger = logging.getLogger('vote')

class BaseElectionView(GenericAPIView):
    """
    Base class for election-specific API views.
    """
    permission_classes = (IsStationStaff, IsAssociatedElection, IsElectionRunning)

    queryset = Election.objects.all()
    lookup_field = 'name'
    lookup_url_kwarg = 'name'

    def get_validated_data(self, request):
        """
        Serializes and validates request data.
        """
        serializer = self.get_serializer_class()(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            if request.user.kind == User.STATION:
                logger.warning('Station %s request invalid', request.user.station.id)
            else:
                logger.warning('Remote user %s request invalid', request.user.username)
            logger.info(serializer.initial_data)
            raise   # Exception handler will handle for us.
        return serializer.validated_data


class BaseElectionEventView(BaseElectionView):
    """
    Base class for remote server callback event views.
    """
    # Note that we don't enforce election state checking, since the callback
    # could be arriving much later. This should not be an issue now, but we'll
    # just document the whole thing.
    permission_classes = (IsRemoteServer,)
