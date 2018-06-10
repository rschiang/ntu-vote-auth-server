from .generics import BaseElectionView
from core.models import Ballot, Session
from django.db.models import Count, Q
from rest_framework.response import Response

class StatisticsView(BaseElectionView):
    """
    Returns election statistics.
    """

    def get(self, request, *args, **kwargs):
        election = self.get_object()
        total = election.sessions.filter(state=Session.VOTED).count()
        values = election.stations.annotate(count=Count('sessions', Q(state=Session.VOTED))).values('name', 'count')

        return Response({
            'status': 'success', 'total': total, 'values': values
        })
