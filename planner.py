from copy import copy
from datetime import datetime, timedelta
from functools import partial
import os
from textwrap import TextWrapper, wrap
import pickle
from collections import namedtuple

from sortedcontainers import SortedDict

import box
import configuration
from time_parser import parse_datetime
from task import TaskList, Task
from terminal_color import style
from utils import rlinput, isint

TaskLocation = namedtuple('TaskLocaiton', ['listkey', 'inlistkey'])

class Calendar:

    def __init__(self):
        self.days = SortedDict()
        list_names = ['inbox', 'later', 'archive', 'trash']
        self.extra_lists = {a:[] for a in list_names}

    def add(self, task, daykey, task_index=None):
        if task_index is None:
            task_index = -1
        if task_index < 0:
            day_len = len(self[daykey])
            task_index += day_len + 1
        self[daykey].insert(task_index, task)

    def pop(self, daykey, task_index):
        self[daykey].pop(task_index)

    def move(self, dest1, dest2):
        task = self.pop(*dest1)
        self.add(task, *dest2)
    
    def schedule(self, dest):
        #today_key = date_to_daykey(datetime.now()))
        #today_index = self.days.bisect_left(today_key)
        # schedule tasklist
        # remove all future indices
        # reinsert tasks
        pass

    @staticmethod
    def date_to_daykey(dt):
        if dt is None:
            dt = datetime.now()
        return (dt-datetime(1970,1,1)).days

    def __getitem__(self, daykey):
        if daykey in self.extra_lists:
            list_ = self.extra_lists[daykey] 
        else:
            daykey= int(daykey)
            if daykey not in self.days:
                self.days[daykey] = []
            list_ = self.days[daykey]
        return list_

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
    def __init__(self, calendar, cal_conf):
        self.cal = calendar
        self.colnum = cal_conf.getint('ColumnNumber')
        self.style1 = cal_conf['LineStyle1']
        self.style2 = cal_conf['LineStyle2']
        self.ansi_styling = cal_conf.getboolean('ActivateAnsiStyling')
        self.headstyles = cal_conf['HeadStyles']
        self.terminstyles = cal_conf['TerminStyles']
        self.donestyles = cal_conf['DoneStyles']
        self.undonestyles = cal_conf['UndoneStyles']
        self.linestyle = box.get_linestyle(self.style1, self.style2)

    def add(self, label, day=None, *, task_index=None, **args):
        #task_index = Calendar.parse_inlistkey(index_str))
        if day==None:
            daykey = 'inbox'
        else:
            date = parse_datetime(day)
            daykey = Calendar.date_to_daykey(date)
        args.update({'label':label})
        self.cal.add(
            daykey=daykey,
            task_index=task_index,
            task=Task(**args))

    def remove(self, arg=''):
        args = arg.split()
        assert len(args)==2
        listkey = self.parse_inlistkey(args[0])
        inlistkey = int(args[1])
        self.cal.pop(listkey, inlistkey)

    def drop(self, arg):
        daykey1, task_index = CalendarInterface.parse_inlistkey(arg)
        if daykey1 == 'trash':
            self.cal.pop(daykey1, task_index)
        else:
            if daykey1 == 'inbox':
                daykey2 = 'later'
            elif daykey1 == 'later':
                daykey2 = 'archive'
            elif daykey1 == 'archive':
                daykey2 = 'trash'
            else:
                daykey2 = 'inbox'
            self.cal.move((daykey1, task_index),(daykey2, -1))

    def push(self, arg=''):
        daykey, task_index = CalendarInterface.parse_inlistkey(arg)
        if daykey == 'inbox':
            next_dk = 0
        elif daykey == 'later':
            next_dk = 'inbox'
        elif daykey == 'archive':
            next_dk = 'later'
        elif daykey == 'trash':
            next_dk = 'archive'
        else:
            next_dk = int(daykey)+1
        self.cal.move((daykey, task_index), (next_dk, -1))

    def do(self, arg=''):
        daykey, task_index = CalendarInterface.parse_inlistkey(arg)
        print(self.cal[daykey])
        self.cal[daykey][task_index].do()

    def undo(self, arg=''):
        daykey, task_index = CalendarInterface.parse_inlistkey(arg)
        self.cal[daykey][task_index].undo()

    def show(self, init_listkey=None):
        if init_listkey is None:
            init_listkey = ''
        print()
        print(self.render(init_listkey))
        print()

    def create(self, arg):
        if arg == 'config':
            conf = configuration.load_configuration()
            configuration.save_configuration(conf)
        else:
            raise ValueError('Unkonwn argument for create!' + str(arg))

    def render(self, init_date):
        inbox = False
        if init_date == 'inbox':
            taskss = [self.cal['inbox']]
            heads  = ['Inbox']
        else :
            if isinstance(init_date, str):
                init_date = parse_datetime(init_date)

            key = Calendar.date_to_daykey(init_date)
            taskss = [self.cal[k] for k in range(key, key+self.colnum)]
            heads = [(init_date + timedelta(days=i)).strftime('%a %d. %b') for i in range(self.colnum)]

        explicite = [[t for t in tasks if t.termin] for tasks in taskss]
        implicite = [[t for t in tasks if not t.termin] for tasks in taskss]
        return self._render(heads, explicite, implicite)


    def _render(self, heads, explicite, implicite):
        assert len(heads)==len(explicite)==len(implicite)

        # initialize constantsrender
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
            
       # add hspace under explicite tasks            
        for col, ex, im in zip(columns, explicite, implicite):
            if ex and im: col.append(empty)

        # add implicite
        for col, tasks in zip(columns, implicite):
            for i,t in enumerate(tasks):
                if len(tasks)<10:
                    indent = str(i) + ' '
                else:
                    indent = str(i).zfill(2) + ' '
                cells = fillup(wrap(t.label, width=colwidth, initial_indent=indent))
                if t.done:
                    style(cells, self.donestyles)
                else:
                    style(cells, self.undonestyles)
                col.extend(cells)

        # set all columns to same length
        type(self)._equalize_columns(columns, filler=empty)
         
        # join columns to output string
        lines = []
        for i, line in enumerate(zip(*columns)):
            if i == horzline_index:
                line = self.linestyle['junction'].join(line)
            else:
                line = self.linestyle['vertical'].join(line)
            lines.append(line)

        return '\n'.join(lines)

    def parse_inlistkey(self, arg):
        if isint(arg):
            relative_days = int(arg)
            inlistkey = relative_days + (datetime.now()-datetime(1970,1,1)).days
        else:
            inlistkey = arg.strip()
        
        return inlistkey

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


def parse_command_parameters(args, varnames, sep='='):
    args = [a.split(sep) for a in args]
   
    parameters = {}
    
    # positional arguments
    allow_positional = True
    for i,a in enumerate(args):
        if len(a)==1:
            if not allow_positional:
                raise SyntaxError('non-keyword arg after keyword arg')
            parameters[varnames[i]] = a[0].strip()
        elif len(a)==2:
            if not allow_positional:
                allow_positional = False
            parameters[a[0].strip()] = a[1].strip()
        else:
            raise SyntaxError('Only one separation character allowed!')

    return parameters
    

        

if __name__ == '__main__':
    
    import sys
   
    # show tasks if no input argument 
    if len(sys.argv) == 1:
        command = 'show'
        args = []
    else:
        command = sys.argv[1]
        args = sys.argv[2:]
    
    # separate arguments with commans instead whitespace 
    args = ' '.join(args)
    args = args.split(',') if args else []

    try:
        cal = Calendar.load()
    except FileNotFoundError:
        print('No calendar file found! Create new ´.planner/cal´.')
        cal = Calendar()

    conf = configuration.load_configuration()
    cali = CalendarInterface(cal, conf['CalendarInterface'])
    func = cali.__class__.__dict__[command]
    #import ipdb; ipdb.set_trace()
    params = parse_command_parameters(args, func.__code__.co_varnames[1:])    
    func(cali, **params)
    cal.save()

    """
    if command == 'add':
        cali.add(**paras)
    elif command == 'do':
        cali.do(**paras)
    elif command == 'undo':
        cali.undo(' '.join(args))
    elif command == 'edit':
        cali.edit(' '.join(args))
    elif command == 'push':
        cali.push(' '.join(args))
    elif command == 'pull':
        cali.pull(' '.join(args))
    elif command == 'list':
        print(cali.render(' '.join(args)))
    """
 



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
