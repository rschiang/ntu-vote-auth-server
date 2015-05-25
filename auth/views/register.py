from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import check_prerequisites
from core.views.utils import error, logger

@api_view(['POST'])
@check_prerequisites('username', 'password')
def register(request):
    pass
