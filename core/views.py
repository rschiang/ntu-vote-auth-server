import re
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

    if VoteEntry.objects.filter(student_id=student_id).count() > 0:
        return Response({"status": "error", "reason": "duplicate_entry"}, status=status.HTTP_400_BAD_REQUEST)

    # We haven't made our connection to ACA
    kinds = {
        '1': '文學院',
        '2': '理學院',
        '3': '社會科學院',
        '4': '醫學院',
        '5': '工學院',
        '6': '生物資源暨農學院',
        '7': '管理學院',
        '8': '公共衛生學院',
        '9': '電機資訊學院',
        'A': '法律學院',
        'B': '生命科學院',
    }

    kind = student_id[3]

    if not (re.match(r'[A-Z]\d{2}[0-9AB]\d{6}', student_id) and kind in kinds):
        return Response({"status": "error", "reason": "invalid_card"}, status=status.HTTP_400_BAD_REQUEST)

    code = AuthCode.objects.filter(kind=kind+'1', issued=False).first()
    if code:
        entry = VoteEntry()
        entry.student_id = student_id
        entry.save()

        code.issued = True
        code.save()
    else:
        return Response({"status": "error", "reason": "out_of_auth_code"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({"status": "success", "uid": student_id, "type": kinds[kind], "code": code.code})
