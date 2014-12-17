# Meta
# Define all election (per-event) related information

import os
import datetime

COLLEGE_NAMES = {
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

COLLEGE_IDS = { value : key for key, value in COLLEGE_NAMES.items() }

KINDS = {
    (college + str(coop)):
        COLLEGE_NAMES[college] + ('（合作社員）' if coop == 1 else '')
    for college in COLLEGE_NAMES.keys()
    for coop in range(2)
}

ENFORCE_EVENT_DATE = os.environ.get('ENFORCE_EVENT')
EVENT_START_DATE = datetime.datetime(2014, 12, 19, 8, 0, 0)
EVENT_END_DATE = datetime.datetime(2014, 12, 19, 20, 0, 0)
