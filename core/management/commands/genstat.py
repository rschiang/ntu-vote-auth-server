import json
import io
from account.models import Station
from core.models import AuthToken
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime

# Helper classes
class Table(object):
    def __init__(self, rows=None, cols=None, default=0):
        self.data = { row: { col: default for col in cols } for row in rows }
        self.rows = list(rows)
        self.cols = list(cols)

    def get(self, x, y):
        return self.data[x][y]

    def set(self, x, y, value):
        self.data[x][y] = value

    def increase(self, x, y):
        self.data[x][y] += 1

    def print_out(self, x_transform=None, y_transform=None, print_sum=False):
        x_transform = x_transform or (lambda x: x)
        y_transform = y_transform or (lambda y: y)
        if print_sum:
            x_sum, y_sum = self.sum()
            self.rows = sorted(self.rows, key=lambda i: x_sum[i], reverse=True)

        entity = {}
        entity['fields'] = [y_transform(y) for y in self.cols]
        entity['items'] = [{
            'name': x_transform(x),
            'values': [self.data[x][y] for y in self.cols],
            } for x in self.rows]

        if print_sum:
            entity['items'].append({'sum': [y_sum[y] for y in self.cols]})

        return entity

    def sum(self):
        x_sum = { row: 0 for row in self.rows }
        y_sum = { col: 0 for col in self.cols }
        for x in self.rows:
            for y in self.cols:
                val = self.data[x][y]
                x_sum[x] += val
                y_sum[y] += val
        return x_sum, y_sum

    def aggregate(self):
        for x in self.rows:
            count = 0
            for y in self.cols:
                count += self.data[x][y]
                self.data[x][y] = count

    def transpose(self):
        self.data = { y: { x: self.data[x][y] for x in self.rows } for y in self.cols }
        self.rows, self.cols = self.cols, self.rows

    @classmethod
    def generate(cls, items, row_attr, rows, col_attr, cols, default=0):
        table = cls(rows=rows, cols=cols, default=default)
        for item in items:
            table.increase(item.__dict__[row_attr], item.__dict__[col_attr])
        return table

class Item(object):
    def __init__(self, token=None):
        self.standing = normalize_standings(token.student_id[0])
        self.college = token.student_id[3]
        self.station_id = token.station_id
        self.time_index = calculate_time_index(localtime(token.timestamp))


# Set up Django environment

# Utility functions
def calculate_time_index(t):
    return t.hour * 2 + (1 if t.minute >= 30 else 0)

def time_index_to_str(i):
    digit = ((i - 24) if i >= 26 else i) / 2
    half = ':30' if i % 2 == 1 else ''
    noon = 'pm' if i >= 24 else 'am'
    return '{}{}{}'.format(digit, half, noon)

def normalize_standings(s):
    if s in STANDINGS.keys():
        return s
    elif s in 'AC':
        return 'T'
    elif s in 'JEQ':
        return 'P'
    elif s == 'F':
        return 'D'
    elif s == 'M':
        return 'R'
    else:
        sys.stderr.write('WARN: Unknown standing {}'.format(s))

# Pre-generate constants
STATIONS = { station.external_id: station.name for station in Station.objects.all() }  # noqa: E305
START_TIME_INDEX = calculate_time_index(settings.EVENT_START_DATE) - 1
END_TIME_INDEX = calculate_time_index(settings.EVENT_END_DATE) + 1
COLLEGES = {
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
}  # noqa: E133
STANDINGS = {
    'B': '大學部',
    'R': '碩士班',
    'D': '博士班',
    'T': '交換/訪問生',
    'P': '在職/進修生',
}  # noqa: E133

class Command(BaseCommand):
    help = 'Generates vote statistics'

    def handle(self, *args, **options):
        doc = {}
        items = [Item(token) for token in AuthToken.objects.filter(issued=True)]

        def station_key_func(x):
            return STATIONS[x]

        def college_key_func(x):
            return COLLEGES[x]

        st_table = Table.generate(items, 'station_id', STATIONS.keys(), 'time_index', range(START_TIME_INDEX, END_TIME_INDEX + 1))
        doc['station-time'] = st_table.print_out(station_key_func, time_index_to_str, print_sum=True)

        st_table.aggregate()
        doc['station-time-aggr'] = st_table.print_out(station_key_func, time_index_to_str, print_sum=False)

        sc_table = Table.generate(items, 'station_id', STATIONS.keys(), 'college', COLLEGES.keys())
        doc['station-college'] = sc_table.print_out(station_key_func, college_key_func, print_sum=True)

        sc_table.transpose()
        doc['college-station'] = sc_table.print_out(college_key_func, station_key_func, print_sum=True)

        ss_table = Table.generate(items, 'station_id', STATIONS.keys(), 'standing', STANDINGS.keys())
        doc['station-standing'] = ss_table.print_out(station_key_func, lambda y: STANDINGS[y], print_sum=True)

        buf = io.StringIO()
        json.dump(doc, buf, ensure_ascii=False, indent=2)
        self.stdout.write(buf.getvalue())
