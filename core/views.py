from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import VoteEntry, AuthCode

def index(request):
    return HttpResponse('It works!')

@api_view(['GET', 'POST'])
def api(request):
    try:
        internal_id = request.DATA['cid']
        student_id = request.DATA['uid']
    except KeyError:
        return Response({"status": "error", "reason": "params_invalid"}, status=status.HTTP_400_BAD_REQUEST)

    if VoteEntry.objects.filter(Q(internal_id=internal_id) | Q(student_id=student_id)).count() > 0:
        return Response({"status": "error", "reason": "duplicate_entry"}, status=status.HTTP_400_BAD_REQUEST)

    code = AuthCode.objects.filter(issued=False).first()
    if code:
        entry = VoteEntry()
        entry.internal_id = internal_id
        entry.student_id = student_id
        entry.save()

        code.issued = True
        code.save()
    else:
        return Response({"status": "error", "reason": "out_of_auth_code"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({"status": "success", "code": code.code})
