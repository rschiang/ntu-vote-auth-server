# Meta information for ACA

AUTHENTICATION_ERRORS = (
    ('發卡次數不一致', 'revision_mismatch'),
    ('為黑名單', 'card_blacklisted'),
    ('沒有啟用卡片資料', 'card_invalid'),
    ('在卡務中不存在', 'card_invalid'),
    ('尚未啟用', 'card_invalid'),
    ('卡片已失效', 'card_invalid'),
    ('查無學號資料', 'student_not_found'),
    ('無持卡人資料', 'student_not_found'),
)

SERVICE_ERRORS = (
    ('未授權', 'unauthorized'),
    ('輸入資料錯誤', 'params_invalid'),
)

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
    '進修推廣學院': 'E',
    '共教中心': 'H',

    # School of Professional Studies
    '牙醫專業學院': '4',
    '藥學專業學院': '4',
    '獸醫專業學院': '6',
}
