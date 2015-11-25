from copy import copy
from datetime import datetime, timedelta
from functools import partial
import os
from textwrap import TextWrapper, wrap
import pickle


from sortedcontainers import SortedDict

import box
import configuration
from task import TaskList, Task, parse_datetime
from terminal_color import style
from utils import rlinput

class Calendar:
    def __init__(self):
        self.days = SortedDict()


    def add(self, task):
        if task.termin:
            dt = task.termin
        else:
            dt = task.schedule_time

        if dt is None:
            self.unsorted.append(task)
        else:
            key = (dt-datetime(1970,1,1)).days
            self[key].append(task)


    def get_task(self, day_index=None, task_index=None):
        day = self.get_day(day_index)
        index = 0
        for task in day:
            if task.termin:
                continue
            if index == task_index:
                return task
        raise IndexError('list index out of range')


    def get_day(self, index=None):
        if index == 'unsorted':
            list_ = self.unsorted
        else:
            list_ = self.days[index]
    return list_


    @staticmethod
    def parse_task_index(arg):
        args = list(filter(arg.split()))
        relative_days = None
        task_index = None
        if len(args) >= 1:
            task_index = int(args[0])
        if len(args) >= 2:
            relative_days = int(args[1])
        day_index = relative_days + (datetime.now()-datetime(1970,1,1)).days
        return {'day_index':day_index, 'task_index':task_index}


    def schedule_future(self):
        # get index for key
        # create tasklist for all indieces >= index
        # schedule tasklist
        # remove all future indices
        # reinsert tasks
        pass

    @staticmethod
    def getkey(dt=None):
        if dt is None:
            dt = datetime.now()
        return (dt-datetime(1970,1,1)).days

    def __getitem__(self, index):
        index = int(index)
        if index not in self.days:
            self.days[index] = []
        return self.days[index]

    @classmethod
    def load(cls):
        filepath = os.path.join(configuration.DEFAULT_PATH, 'cal')
        with open(filepath,'rb') as f:
            cal = pickle.load(f)
        assert isinstance(cal, cls)
        return cal

    def save(self):
        path = configuration.DEFAULT_PATH
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, 'cal')
        with open(filepath,'wb') as f:
            pickle.dump(self, f, protocol=3)


class CalendarInterface:
    def __init__(self, Calendar, cal_conf):
        self.cal = cal
        self.colnum = cal_conf.getint('ColumnNumber')
        self.style1 = cal_conf['LineStyle1']
        self.style2 = cal_conf['LineStyle2']
        self.ansi_styling = cal_conf.getboolean('ActivateAnsiStyling')
        self.headstyles = cal_conf['HeadStyles']
        self.terminstyles = cal_conf['TerminStyles']
        self.donestyles = cal_conf['DoneStyles']
        self.undonestyles = cal_conf['UndoneStyles']
        self.linestyle = box.get_linestyle(self.style1, self.style2)

    def add(self, **args):
        #task_index = Calendar.parse_task_index(index_str))
        self.cal.add(task=Task(**args))

    def do(self, arg):
        index_dict = Calendar.parse_task_index(arg)
        self.cal.get_task(**index_dict).do()

    def undo(self, arg):
        index_dict = Calendar.parse_task_index(arg)
        self.cal.get_task(**index_dict).undo()

    def render(self, init_date):
        if isinstance(init_date, str):
            init_date = parse_datetime(init_date)

        key = Calendar.getkey(init_date)
        taskss = [cal[k] for k in range(key, key+self.colnum)]

        heads = [(init_date + timedelta(days=i)).strftime('%A') for i in range(self.colnum)]
        explicite = [[t for t in tasks if t.termin] for tasks in taskss]
        implicite = [[t for t in tasks if not t.termin] for tasks in taskss]
        return self._render(heads, explicite, implicite)


    def _render(self, heads, explicite, implicite):
        assert len(heads)==len(explicite)==len(implicite)

        # initialize constants
        termwidth, _ = os.get_terminal_size()
        colnum = len(heads)
        colwidth = (termwidth+1)//colnum - 1
        empty = ' '*colwidth
        fillup = partial(type(self).fillup, colwidth=colwidth)

        # add head and horizontal line
        wrap1 = TextWrapper(width=colwidth).wrap
        columns = [ fillup(wrap1(h)) for h in heads ]
        for col in columns: style(col, self.headstyles)
        type(self)._equalize_columns(columns, filler=empty)
        horzline_index = len(columns[0])
        horzl = self.linestyle['horizontal']*colwidth
        for col in columns: col.append(horzl)
        
        # add explicite
        for col, tasks in zip(columns, explicite):
            for t in tasks:
                dt = t.termin if t.termin else t.schedule_time
                lines = wrap(
                    text=t.label,
                    width=colwidth,
                    initial_indent=dt.strftime('%M:%S '))
                fillup(lines)
                style(lines, self.terminstyles)
                col.extend(lines)

        # add implicite
        for col, tasks in zip(columns, implicite):
            for i,t in enumerate(tasks):
                if len(tasks)<10:
                    indent = str(1) + ' '
                else:
                    indent = str(i).zfill(2) + ' '
                cells = fillup(wrap(t.label, width=colwidth, initial_indent=indent))
                if task.done:
                    style(cells, self.donestyle)
                else:
                    style(cells, self.donestyle)
                col.extend(cells)

        # set all columns to same length
        type(self)._equalize_columns(columns, filler=empty)

        # join colloms to output string
        lines = []
        for i, line in enumerate(zip(*columns)):
            if i == horzline_index:
                line = self.linestyle['junction'].join(line)
            else:
                line = self.linestyle['vertical'].join(line)
            lines.append(line)

        return '\n'.join(lines)

    @staticmethod
    def _equalize_columns(columns, filler):
        maxlen = max(map(len, columns))
        for col in columns:
            if len(col) == maxlen:
                continue
            col.extend([filler]*(maxlen-len(col)))

    @staticmethod
    def fillup(column, colwidth, side_effect=True):
        """ Append whitespaces to every cell that does not match colwidth."""

        if not side_effect:
            column = copy(column)

        for i,cell in enumerate(column):
            if len(cell) < colwidth:
                column[i] = cell + ' '*(colwidth-len(cell))
        return column

def argjoin(arg):
    if not arg or arg.lower()=='none':
        return None
    if not isinstance(arg, str):
        return ' '.join(arg)
    return arg

def edit_dialog(task):
    for para in ['label','preftime','priority','termin','deadline','duration']:
        if para not in parameters:
            input_ = input(para.capitalize() + ': ')
            if para == 'priority':
                parameters[para] = float(input_)
            else:
                parameters[para] = argjoin(input_)

    task.label = rlinput('Enter label: ', task.label)

    dead_str = rlinput('Enter deadline: ', task.deadline)
    task.deadline = parse_date(dead_str)

    dur_str = rlinput('Enter duration: ', task.duration)
    task.duration = parse_delta(dead_str)

    pref_str = rlinput('Enter preftime: ', task.preftime)
    task.preftime = parse_intervall(dead_str)

    prior_str = rlinput('Enter priority: ', task.priority)
    task.priority = float(prior_str)

    term_str = rlinput('Enter termin: ', task.termin)
    task.termin = parse_date(term_str)


if __name__ == '__main__':
    
    import sys

    if len(sys.argv) == 1:
        command = 'list'
        args = []
    else:
        command = sys.argv[1]
        args = sys.argv[2:]

    try:
        cal = Calendar.load()
    except FileNotFoundError:
        print('No calendar file found! Create new ´.planner/cal´.')
        cal = Calendar()

    conf = configuration.load_configuration()
    cali = CalendarInterface(cal, conf['CalendarInterface'])

    if command == 'add':
        label = ' '.join(args)
        cali.add(label = label)
    elif command == 'do':
        cali.do(' '.join(args))
    elif command == 'undo':
        cali.undo(' '.join(args))
    elif command == 'edit':
        cali.edit(' '.join(args))
    elif command == 'list':
        print(cali.render(' '.join(args)))

    cal.save()
 



"""import argparse
            parser = argparse.ArgumentParser(description='Show calendar.')
            parser.add_argument('command', default='list', help='List tasks.')
            parser.add_argument('--label', nargs='+')
            parser.add_argument('--priority', type=float)
            parser.add_argument('--preftime', nargs='+')
            parser.add_argument('--termin', nargs='+')
            parser.add_argument('--deadline', nargs='+')
            parser.add_argument('--duration', nargs='+')
            parser.add_argument('--do', nargs='+')
            parser.add_argument('--undo', nargs='+')
            parser.add_argument('--dialog', action='store_true')
            parser.add_argument('-a', '--add', nargs='+')
            args = parser.parse_args()
            command = args.command
        
            parameters = {}
            if args.label:
                parameters['label'] = ' '.join(args.label)
            if args.priority:
                parameters['priority'] = float(args.priority)
            if args.preftime:
                parameters['preftime'] = argjoin(args.preftime)
            if args.termin:
                parameters['termin'] = argjoin(args.termin)
            if args.deadline:
                parameters['deadline'] = argjoin(args.deadline)
            if args.duration:
                parameters['duration'] = argjoin(args.duration)"""