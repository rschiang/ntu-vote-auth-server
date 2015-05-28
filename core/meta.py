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

COLLEGE_IDS = {
    # Ordinary colleges
    '文學院': '1',
    '理學院': '2',
    '社會科學院': '3',
    '醫學院': '4',
    '工學院': '5',
    '生物資源暨農學院': '6',
    '管理學院': '7',
    '公共衛生學院': '8',
    '電機資訊學院': '9',
    '法律學院': 'A',
    '生命科學院': 'B',

    # School of Professional Studies
    '牙醫專業學院': '4',
    '藥學專業學院': '4',
    '獸醫專業學院': '6',
}

KINDS = {
    # Colleges
    '10': '文學院',
    '20': '理學院',
    '30': '社會科學院',
    '40': '醫學院',
    '50': '工學院',
    '60': '生物資源暨農學院',
    '70': '管理學院',
    '80': '公共衛生學院',
    '90': '電機資訊學院',
    'A0': '法律學院',
    'B0': '生命科學院',

    # Graduates
    '11': '文學院研究生',
    '21': '理學院研究生',
    '31': '社會科學院研究生',
    '41': '醫學院研究生',
    '51': '工學院研究生',
    '61': '生物資源暨農學院研究生',
    '71': '管理學院研究生',
    '81': '公共衛生學院研究生',
    '91': '電機資訊學院研究生',
    'A1': '法律學院研究生',
    'B1': '生命科學院研究生',

    # Additional combinations
    '01': '獨立學程研究生',
    '4A': '醫學系',
    '5C': '工學院（社科院選區）',
    '6A': '獸醫學系',
    '6B': '獸醫學系（系學會長）',
    '9A': '電機工程學系',
}

UNDERGRADUATE_CODES = (
    'B', # Bachelor
    'T', # Exchange students
    'E', # Professional Education students
)

GRADUATE_CODES = (
    'R', # Master
    'A', # Master exchange students
    'P', # Part-time master students
    'J', # Executive master students
    'M', # Bachelors transfered from doctor degree
    'D', # Doctor
    'C', # Doctor exhange students
    'F', # Bachelors applied for doctor degree
    'Q', # Part-time students of above
)

ENFORCE_EVENT_DATE = os.environ.get('ENFORCE_EVENT')
EVENT_START_DATE = datetime.datetime(2015, 5, 28, 8, 45, 0)
EVENT_END_DATE = datetime.datetime(2015, 5, 28, 19, 15, 0)

SESSION_MAX_RESPOND_TIME = datetime.timedelta(minutes=2)
SESSION_EXPIRE_TIME = datetime.timedelta(hours=12)
