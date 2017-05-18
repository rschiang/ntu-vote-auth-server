#!/usr/bin/env python
import os
from account.models import Station
from core.models import AuthToken
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

        print('[', end='')
        print(*(y_transform(y) for y in self.cols), ']', sep=', ')
        print('{')
        for x in self.rows:
            print('  ', x_transform(x), ': [', end='')
            print(*(self.data[x][y] for y in self.cols), sep=', ', end='')
            print('],')
        if print_sum:
            print('sum: [', end='')
            print(*(y_sum[y] for y in self.cols), sep=', ', end='')
            print('],')
        print('}')

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
        self.standing = token.student_id[:3]
        self.college = token.kind[0]
        self.station_id = token.station_id
        self.time_index = calculate_time_index(token.timestamp) - START_TIME_INDEX


# Set up Django environment
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
from django.conf import settings  # noqa: E402

# Utility functions
def calculate_time_index(t):
    t = localtime(t)
    return t.hour * 2 + (1 if t.minute >= 30 else 0)

def time_index_to_str(i):
    digit = ((i - 24) if i >= 26 else i) / 2
    half = ':30' if i % 2 == 1 else ''
    noon = 'pm' if i >= 24 else 'am'
    return '{}{}{}'.format(digit, half, noon)

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
}

# Table generation
def print_station_time_table():
    table = Table.generate(items, 'station_id', STATIONS.keys(), 'time_index', range(START_TIME_INDEX, END_TIME_INDEX + 1))
    table.print_out(lambda x: STATIONS[x], time_index_to_str, print_sum=True)
    return table

def print_station_college_table():
    table = Table.generate(items, 'station_id', STATIONS.keys(), 'college', COLLEGES.keys())
    table.print_out(lambda x: STATIONS[x], lambda y: COLLEGES[y], print_sum=True)
    return table


if __name__ == '__main__':
    items = [Item(token) for token in AuthToken.objects.filter(issued=True)]

    print('\n<Station-Time>')
    station_time_table = print_station_time_table()
    station_time_table.aggregate()
    print('\n<Station-Time-Aggr>')
    station_time_table.print_out(lambda x: STATIONS[x], time_index_to_str, print_sum=False)

    print('\n<Station-College>')
    station_college_table = print_station_college_table()
    station_college_table.transpose()
    print('\n<College-Station>')
    station_college_table.print_out(lambda x: STATIONS[x], lambda y: COLLEGES[y], print_sum=True)
