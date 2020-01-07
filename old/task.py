from datetime import datetime, timedelta
import dateutil.parser
import os
import schedule
import re

_delta_regex = re.compile(r'((?P<weeks>\w+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def parse_timedelta(time_str):
    parts = _delta_regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def parse_datetime(time_str):
    time_str = time_str.strip()
    try:
        num = int(time_str)
        dt = (datetime.today()+timedelta(days=num))
    except ValueError:
        dt = dateutil.parser.parse(time_str)
    return dt


class Task:
    def __init__(self, label, deadline=None, duration=None, preftime=None, priority=1, termin=None):
        
        self.label = label 
        self.deadline = deadline
        self.duration = duration
        self.preftime = preftime # preferred time intervall
        self.priority = priority
        self.termin = termin

        self.done = False
        self.schedule_time = None


    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, dead):
        if isinstance(dead, str):
            try :
                self._deadline = parse_datetime(dead)
            except ValueError as ve:
                raise ValueError('Could not parse deadline string: '\
                 + str(dead) + '\n' + str(ve))
        else:
            self._deadline = dead

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, dur):
        if isinstance(dur, dict):
            self._duration = timedelta(**dur)
        elif isinstance(dur, str):
            self._duration = parse_timedelta(dur)
        else:
            self._duration = dur

    @property
    def preftime(self):
        return self._preftime

    @preftime.setter
    def preftime(self, pt):
        if isinstance(pt, str):
            self._preftime = TimeIntervall.fromstring(pt)
        else:
            self._preftime = pt

    @property
    def priority(self): 
        return self._priority

    @priority.setter
    def priority(self, p):
        assert p > 0
        self._priority = p

    @property
    def termin(self):
        return self._termin

    @termin.setter
    def termin(self, termin):
        if isinstance(termin, str):
            try :
                self._termin = parse_datetime(termin)
            except ValueError as error:
                raise ValueError('Could not parse deadline string: '\
                 + str(termin) + '\n' + str(error))
        else:
            self._termin = termin

    def do(self):
        self.done = True

    def undo(self):
        self.done = False

    def __str__(self):
        out = (
            ('Task', id(self)),
            ('label', self.label),
            ('deadline', self.deadline),
            ('duration', self.duration),
            ('preftime', self.preftime),
            ('priority', self.priority),
            ('termin', self.termin),
            ('done', self.done),
            ('schedule_time', self.schedule_time),
        )
        return '\n  '.join([' : '.join([str(r) for r in row]) for row in out])

    def key_func(self):
        return self.schedule_time


class TimeIntervall:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @classmethod
    def fromstring(cls, string):
        string = string.lower().replace('_',' ')
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        if string == 'today':
            start = today
            end = today + timedelta(days=1)
        elif string == 'tomorrow':
            start = today + timedelta(days=1)
            end = today + timedelta(days=2)
        elif string == 'day_after_tomorrow':
            start = today + timedelta(days=2)
            end = today + timedelta(days=3)
        elif string == 'yesterday':
            start = today - timedelta(days=1)
            end = today
        elif string == 'this week':
            start = today - timedelta(days=today.weekday())
            end   = start + timedelta(days=7)
        elif string == 'next week':
            start = today + timedelta(days=7) - timedelta(days=today.weekday())
            end   = start + timedelta(days=7)
        elif string == 'last week':
            start = today - timedelta(days=7) - timedelta(days=today.weekday())
            end   = start + timedelta(days=7)
        else:
            try:
                str1, str2 = string.split('-')
                start = parse_datetime(str1)
                end = parse_datetime(str2)
            except Exception as e:
                raise ValueError('Input Sting \"' + str(string) + '\" could not be interpreted! ... ' + str(e))

        return TimeIntervall(start, end)

    def __str__(self):
        return ' -- '.join([str(self.start), str(self.end)])


class TaskList:
    def __init__(self):
        self._list = []

    def add(self, *tasks):
        for task in tasks:
            self._list.append(task)

    def schedule(self):
        schedule.schedule(self._list)

    @classmethod
    def load(cls, filepath):
        filepath = os.path.expanduser(filepath)
        with open(filepath) as f:
            code = f.read()
        task_dict = yaml.load(code)
        print(task_dict)
        
    def save(self, filepath):
        filepath = os.path.expanduser(filepath)
        code = yaml.dump(self._list)
        with open(filepath,'w') as f:
            f.write(code)
        

