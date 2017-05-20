import sys
from account.models import Station
from core.models import AuthToken
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime
from functools import reduce

# Helper classes
class Table(object):
    def __init__(self):
        self.data = {}

    def get(self, x, y):
        return self.data[x][y]

    def set(self, x, y, value):
        try:
            self.data[x][y] = value
        except KeyError:
            self.data[x] = { y: value }

    def increase(self, x, y):
        try:
            self.data[x][y] += 1
        except KeyError:
            if x not in self.data:
                self.data[x] = { y: 1 }
            elif y not in self.data[x]:
                self.data[x][y] = 1

    def aggregate(self):
        for x in self.data:
            count = 0
            for y in sorted(self.data[x].keys()):
                count += self.data[x][y]
                self.data[x][y] = count

    def transpose(self):
        data = self.data
        y_keys = reduce((lambda a, b: set(a).union(b)), (data[x].keys() for x in data))
        self.data = { y: { x: data[x][y] for x in data } for y in y_keys }

    @classmethod
    def generate(cls, items, row_attr, col_attr):
        table = cls()
        for item in items:
            table.increase(item.__dict__[row_attr], item.__dict__[col_attr])
        return table

class Item(object):
    def __init__(self, token, stations):
        self.standing = normalize_standings(token.student_id[:3])
        self.college = token.student_id[3]
        self.station = stations[token.station_id]
        t = localtime(token.timestamp)
        self.time = '{:02}:{:02}'.format(t.hour, 30 if t.minute >= 30 else 0)

# Utility functions
def normalize_standings(standing):
    s = standing[0]
    if s == 'B':
        return standing  # Include grade for better categorization
    elif s in 'RDTP':
        return s         # Standard standings
    elif s in 'AC':
        return 'T'       # Merge graduate exchange students with bachelor
    elif s in 'JEQ':
        return 'P'       # Various continuing studies
    elif s == 'F':
        return 'D'       # Bachelors applied directly for doctors
    elif s == 'M':
        return 'R'       # Doctors transfering to master classes
    else:
        sys.stderr.write('WARN: Unknown standing {}'.format(s))

class Command(BaseCommand):
    help = 'Generates vote statistics'

    def add_arguments(self, parser):
        parser.add_argument('x', help='name of first dimensional data')
        parser.add_argument('y', help='name of second dimensional data')

    def handle(self, *args, **options):
        stations = { station.external_id: station.name for station in Station.objects.all() }
        items = [Item(token, stations=stations) for token in AuthToken.objects.filter(issued=True)]

        row_attr = options['x']
        col_attr = options['y']

        table = Table.generate(items, row_attr, col_attr)
        fp = self.stdout
        fp.write(row_attr, ending=',')
        fp.write(col_attr, ending=',')
        fp.write('count')
        for x in sorted(table.data.keys()):
            inner = table.data[x]
            for y in sorted(inner.keys()):
                fp.write(x, ending=',')
                fp.write(y, ending=',')
                fp.write(str(inner[y]))
