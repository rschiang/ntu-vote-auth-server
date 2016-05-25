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
    'H': '共同教育中心',
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
    '共同教育中心': 'H',

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
    'H0': '共同教育中心研究生',

    # Additional combinations
    '3A': '政治學系',
    '4A': '醫學系',
    '6A': '生物產業機電工程學系',
    '6B': '生物產業機電工程學所',

    # Double majors
    '1S': '文學院（雙主修政治系）',
    '3S': '社會科學院（雙主修政治系）',
    '4T': '醫學系（雙主修政治系）',
    '5S': '工學院（雙主修政治系）',
    '6S': '生物資源暨農學院（雙主修政治系）',
    '7S': '管理學院（雙主修政治系）',
    '9S': '電機資訊學院（雙主修政治系）',
    'AS': '法律學院（雙主修政治系）',
}

UNDERGRADUATE_CODES = (
    'B',  # Bachelor
    'T',  # Exchange students
    'E',  # Professional Education students
)

GRADUATE_CODES = (
    'R',  # Master
    'A',  # Master exchange students
    'P',  # Part-time master students
    'J',  # Executive master students
    'M',  # Bachelors transfered from doctor degree
    'D',  # Doctor
    'C',  # Doctor exhange students
    'F',  # Bachelors applied for doctor degree
    'Q',  # Part-time students of above
)

# Departments who opt to join election
JOINT_DEPARTMENT_CODES = (
    '3021', '3022', '3023', # Department of Political Science
    '4010',  # Department of Medicine
    '6110',  # Department of Bio-industrial Mechatronics Engineering
    '6310',  # Grad. Institute of Bio-industrial Mechatronics Engineering
)

ENFORCE_EVENT_DATE = os.environ.get('ENFORCE_EVENT')
EVENT_START_DATE = datetime.datetime(2016, 5, 26, 8, 45, 0)
EVENT_END_DATE = datetime.datetime(2016, 5, 26, 19, 15, 0)

SESSION_MAX_RESPOND_TIME = datetime.timedelta(minutes=2)
SESSION_EXPIRE_TIME = datetime.timedelta(hours=12)
