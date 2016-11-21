from core.models import Entry
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import scheduled, login_required, permission
from account.models import User, Station, Session
from core.views.utils import logger


@api_view(['GET'])
@login_required
@permission(User.ADMIN)
def list_entry(request):
    return Response({
        'status': 'success',
        'entrys': [{
            'id': e.id,
            'name': e.name,
            'dpt_code': e.dpt_code,
            'kind': e.kind,
        } for e in Entry.objects.all()],
    })


@api_view(['POST'])
@login_required
@permission(User.ADMIN)
@check_prerequisites('kind', 'dpt_code', 'name')
def create_entry(request):

    try:
        entry = Entry.objects.create(
                    kind=request.data['kind'],
                    kind=request.data['dpt_code'],
                    kind=request.data['name']
                )
        entry.save()
    except:
        return error('add_fail')

    # Log this event
    logger.info('Admin %s create entry %s(%s)', request.user.username, entry.name, entry.dpt_code)

    return Response({
        'status': 'success',
        'entrys': {
            'id': entry.id,
            'name': entry.name,
            'dpt_code': entry.dpt_code,
            'kind': entry.kind,
        },
    })


@api_view(['GET'])
@login_required
@permission(User.ADMIN)
def retrieve_entry(request, entry_id):

    try:
        entry = Entry.objects.get(id=entry_id)
    except:
        return error('entry_not_found', status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'status': 'success',
        'entrys': {
            'id': entry.id,
            'name': entry.name,
            'dpt_code': entry.dpt_code,
            'kind': entry.kind,
        }
    })

@api_view(['POST', 'UPDATE'])
@login_required
@permission(User.ADMIN)
@check_prerequisites('kind', 'dpt_code', 'name')
def update_entry(request, entry_id):

    try:
        entry = Entry.objects.get(id=entry_id)
    except:
        return error('entry_not_found', status=status.HTTP_404_NOT_FOUND)

    entry.dpt_code = request.data['dpt_code']
    entry.name = request.data['name']
    entry.kind = request.data['kind']

    entry.save()
    
    # Log this event
    logger.info('Admin %s update entry %s(%s)', request.user.username, entry.name, entry.dpt_code)

    return Response({
        'status': 'success',
        'entrys': {
            'name': entry.name,
            'dpt_code': entry.dpt_code,
            'kind': entry.kind,
        },
    })

@api_view(['GET', 'DELETE'])
@login_required
@permission(User.ADMIN)
def delete_entry(request):

    try:
        entry = Entry.objects.create()
    except:
        return error('entry_not_found', status=status.HTTP_404_NOT_FOUND)

    # Log this event
    logger.info('Admin %s delete entry %s(%s)', request.user.username, entry.name, entry.dpt_code)

    entry.delete()
    
    return Response({
        'status': 'success',
    })
