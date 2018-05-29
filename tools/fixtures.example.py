#!/usr/bin/env python
from account.models import User
from core.models import Ballot, Condition, Election, Elector, Station, Session
from django.db import transaction

"""
Example fixtures of a proper election.
Customizable UI frontend is expected in the next milestone.
"""

BALLOTS = [
    # name, description, foreign_id, conditions, electors
    ('學生會長', '學生會會長', 1,
        [], []),
    ('文學院學生代表', '學生代表大會文學院學生代表', 2,
        [('college', '1')],
        [('B06101001', False)]),
    ('理學院學生代表', '學生代表大會理學院學生代表', 3,
        [('college', '2')], []),
    ('社科院學生代表', '學生代表大會社會科學院學生代表', 4,
        [('college', '3')],
        [('B06101001', True)]),
    ('醫學院學生代表', '學生代表大會醫學院學生代表', 5,
        [('college', '4')], []),
    ('工學院學生代表', '學生代表大會工學院學生代表', 6,
        [('college', '5')], []),
    ('生農學院學生代表', '學生代表大會生物資源暨農學院學生代表', 7,
        [('college', '6')], []),
    ('管理學院學生代表', '學生代表大會管理學院學生代表', 8,
        [('college', '7')], []),
    ('公衛學院學生代表', '學生代表大會公衛學院學生代表', 9,
        [('college', '8')], []),
    ('電資學院學生代表', '學生代表大會電資學院學生代表', 10,
        [('college', '9')], []),
    ('法律學院學生代表', '學生代表大會法律學院學生代表', 11,
        [('college', 'A')], []),
    ('性平會學生委員', '性別平等委員會學生委員', 12,
        [], []),
    ('研協會長', '研究生協會會長', 13,
        [('standing', 'R')], []),
    ('研究生代表', '研究生協會研究生代表', 14,
        [('standing', 'R')], []),
    ('文學院學生會長', '文學院學生會會長', 15,
        [('college', '1')], []),
    ('社科院學生會長', '社會科學院學生會會長', 16,
        [('college', '3')], []),
    ('生農院學生會長', '生物資源暨農學院學生會會長', 17,
        [('college', '6')], []),
    ('法律系學生會長', '法律學系學生會會長', 18,
        [('college', 'A'), ('standing', 'B')], []),
    ('醫學系正副學生會長', '醫學系學生會正、副會長', 19,
        [('department', '4010'), ('standing', 'B')], []),
]

STATIONS = [
    # name, description, foreign_id
    ('活大', '第一學生活動中心', 1),
    ('二活', '第二學生活動中心', 2),
    ('共同', '共同教學館', 3),
    ('博雅', '博雅教學館', 4),
    ('新生', '新生教學館', 5),
    ('頤賢', '社會科學院頤賢館', 6),
    ('男一', '長興街男一舍', 7),
    ('大一女', '大一女', 8),
    ('水源', '水源校區', 9),
    ('醫圖', '醫學院圖書館前', 10),
    ('公衛', '公衛學院', 11),
    ('校門', '校門口大學廣場旁', 12),
]

# These people aren't allowed to vote due to remote voting registration
BANNED_STUDENTS = [
    'B00000000',
]

@transaction.atomic
def populate_db():
    # Create the Election
    election = Election.objects.create(name='106-2', description='106-2 臺大十合一學生選舉')

    # Create accounts
    User.objects.create_user('vote', kind=User.REMOTE_SERVER)

    count = 0
    for name, description, foreign_id in STATIONS:
        count += 1
        username = 'vote{:02}'.format(count)
        password = User.objects.make_random_password()
        user = User.objects.create_user(username, password=password, kind=User.STATION)
        station = Station.objects.create(election=election, foreign_id=foreign_id, user=user, name=name, description=description)
        print(station.id, station.name, username, password)

    # Create ballots
    for name, description, foreign_id, conditions, electors in BALLOTS:
        ballot = Ballot.objects.create(election=election, foreign_id=foreign_id, name=name, description=description)
        print(ballot)
        # Create conditions
        if len(conditions) > 1:
            condition = Condition.objects.create(ballot=ballot, field=Condition.MATCH_ALL)
            for field, value in conditions:
                Condition.objects.create(ballot=ballot, parent=condition, field=field, value=value)
        elif conditions:
            field, value = conditions[0]
            Condition.objects.create(ballot=ballot, field=field, value=value)
        # Add elector overrides
        for student_id, is_allowed in electors:
            elector = Elector.objects.create(ballot=ballot, student_id=student_id, is_allowed=is_allowed)
            print(elector)

    # Ban students
    for student_id in BANNED_STUDENTS:
        Session.objects.create(election=election, student_id=student_id, state=Session.BANNED)
