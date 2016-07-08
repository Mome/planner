try:
    import pulp
except Exception as e:
    # print(e)
    pass

from datetime import datetime, timedelta
from itertools import accumulate, product
from math import ceil, exp
from functools import partial

def schedule(tasks):

    # create worktime function
    wtf = get_linear_wtf(
        start_slot=8*12,
        end_slot=18*12,
        tolerance=2*12,
        baseline=0.1,
    )

    # create urgency function
    uf = get_harmonic_urgfunc(
        max_urg=10,
        decay=0.001,
    )

    # create task fittness function
    task_fitness = get_task_fittness(
        worktime_func = wtf,
        urgency_func = uf,
        preftime_weight = 0.7,
        max_early_bonus= 0.5,
        early_bonus_decay = 0.001
    )

    scheduler = Scheduler(task_fitness)
    assignment = scheduler.schedule(tasks)
    return assignment


def get_linear_wtf(start_slot, end_slot, tolerance, baseline):

    base_end = start_slot-tolerance
    base_start = end_slot+tolerance

    a1 = (1-baseline)/(start_slot-base_end)
    b1 = baseline - a1*base_end

    a2 = -a1
    b2 = baseline - a2*base_start

    def lwtf(slot):
        if start_slot <= slot <= end_slot:
            return 1
        if slot <= base_end or base_start <= slot:
            return baseline
        if slot < start_slot:
            return a1*slot + b1
        else:        
            return a2*slot + b2

    return lwtf


def get_exponential_urgfunc(max_urg, urg_influence):
    
    def urgfunc(x):
        #print('exponent:', -urg_influence*x)
        try:
            return max_urg*exp(-urg_influence*x)
        except OverflowError:
            return float('inf')

    return urgfunc


def get_harmonic_urgfunc(max_urg, decay):
    
    def urgfunc(x):
        if x < 0:
            return max_urg*(1-x*decay)

        return max_urg/(1+x*decay)

    return urgfunc


def get_task_fittness(worktime_func, urgency_func, preftime_weight, max_early_bonus, early_bonus_decay, now=None):

    if now is None:
        now = SlotDate.now().abslot

    # generate cummulative worktime array
    wta = [worktime_func(i) for i in range(SlotDate.slots_per_day)]
    cwta = list(accumulate(wta))
    
    tff = partial(timefit, cwta=cwta, ptw=preftime_weight)
    
    # generate urgency function
    urf = partial(urgency, urgfunc=urgency_func)

    def task_fitness(task, sched_slot):
        urg = urf(task, sched_slot)
        if urg == 0.0:
            return float('inf')

        timefit = tff(task.preftime, task.duration, sched_slot)

        early_bonus = early_bonus_func(sched_slot, now, max_early_bonus, early_bonus_decay)

        return task.priority*(timefit / urg + early_bonus)

    return task_fitness


def timefit(preftime, duration, sched_sd, cwta, ptw, version=1):

    intervall = SlotIntervall.span(sched_sd, duration)

    if version is 1:
        if intervall.days: # day overflow
            tf_sum = cwta[-1]*(intervall.days-1)
            tf_sum += (cwta[-1] - cwta[intervall.start.slot]) + cwta[intervall.end.slot]
        else:
            tf_sum = cwta[intervall.end.slot] - cwta[intervall.start.slot]

        if preftime:
            ol_num = preftime.count_overlap(intervall)
            tf_sum = ol_num*ptw + tf_sum*(1-ptw)

        return tf_sum / intervall.slots

    if version is 2:
        ...


def urgency(task, sceduled_time, urgfunc):
    if task.deadline:
        if task.duration:
            dur = task.duration
        else:
            dur = default_duration

        #print('\ndead', task.deadline,
        #      '\nsced', SlotDate.fromabslot(sceduled_time),
        #      '\ndur', dur*5)
        urg = urgfunc(int(task.deadline)-sceduled_time-dur)

    else:
        urg = 1
    
    return urg


def early_bonus_func(sched_sd, now, max_bonus, decay):
    diff = abs(sched_sd - now)
    return max_bonus / (diff*decay + 1)


def check_constraints(sched_times, tasks, termins):
    """For unconstrained solver. Returns inf for contrainst are not met."""

    sched_intervals = list(zip(sched_times,[ s+t.duration for s,t in zip(sched_times,tasks)]))
    termin_starts = [t.termin.abslot for t in termins]
    termin_intervals = list(zip(termin_starts,[ s+t.duration for s,t in zip(termin_starts,termins)]))

    # check tasks overlap with termins
    for si, ti in product(sched_intervals, termin_intervals):
        # if count_overlap(*si,*ti): # requires python 3.5
        if count_overlap(*(list(si)+list(ti))): # python 3.4 version
        
            return False

    # check task overlap witch other tasks
    for si1, si2 in product(sched_intervals, repeat=2):
        if si1 is si2:
            continue
        #if count_overlap(*si1,*si2): # requires python 3.5
        if count_overlap(*(list(si1)+list(si2))): # python 3.4 version
            return False

    return True


fit_call_counter = 0

class Scheduler:
    def __init__(self, task_fittness):
        self.task_fittness = task_fittness

    def schedule(self, tasks, backend='scipy'):

        # extract the termins
        termins = [t for t in tasks if t.termin]
        tasks   = [t for t in tasks if not t.termin]

        # convert to SlotTasks, to round the time
        s_tasks = [SlotTask(t) for t in tasks]
        s_termins = [SlotTask(t) for t in termins]

        backend = backend.lower()
        if backend == 'pulp':
            result = self.schedule_pulp(s_tasks, s_termins)
        elif backend == 'scipy':
            result = self.schedule_scipy(s_tasks, s_termins)
        else:
            raise ValueError('Unknown backend', backend)

        # assign schedules dates to tasks
        dates = [SlotDate.fromabslot(abslot).to_date() for abslot in result]
        for task, date in zip(tasks, dates):
            task.schedule_time = date


    def schedule_scipy(self, tasks, termins):
        from scipy.optimize import differential_evolution

        global fit_call_counter

        def objective(sched_times):
            global fit_call_counter
            fit_call_counter += 1
            if not check_constraints(sched_times, tasks, termins):
                value = -1*float('inf')
            else:
                value = sum(self.task_fittness(t,s) for t,s in zip(tasks, sched_times))
            return -1*value
        
        now = SlotDate.now().abslot
        in_one_month = now+(60//5)*24*30
        bounds = [(now, in_one_month)]*len(tasks)

        result = differential_evolution(objective, bounds)

        print('fit_call_counter', fit_call_counter)
        fit_call_counter = 0

        return result.x


    def schedule_pulp(self, tasks, termins):
        now = SlotDate.now().abslot

        # create a pulp minimization problem
        prob = pulp.LpProblem("Task Sceduling", pulp.LpMinimize)
        variables = [pulp.LpVariable(t.label, now, None, 'Integer') for t in tasks]

        # zip variables and tasks for iteration
        tasks_vars = list(zip(tasks, variables))

        # add objective function
        prob += sum([self.task_fittness(t,v) for t,v in tasks_vars])

        # add constraints for termin overlap
        for (task, var), termin in product(tasks_vars, termins):
            prob += (var <= termin.termin.abslot + termin.duration \
                or termin.termin.abslot <= var+task.duration.slots), "termin overlap"

        # add constraints for task overlap
        for (t1, var1), (t2, var2) in permutations(tasks_vars, 2):
            if t1 is t2:
                continue
            prob += (var2 <= var1+t1.duration or \
                var1 <= var2+t2.duration), "task overlap"

        print('tries to solve')

        # all the action happens here
        prob.solve()

        return tasks_vars


class SlotDate:

    slot_size = 5 # minutes
    assert 60%slot_size==0
    slots_per_hour = 60//slot_size
    slots_per_day  = 24*slots_per_hour

    def __init__(self, days, minutes):
        self.days = days
        self.minutes = minutes
        self.slot = minutes // SlotDate.slot_size
        #self.abslot = (datetime(1970,1,1) + timedelta(days=days, minutes=minutes))
        self.abslot = days*SlotDate.slots_per_day + self.slot

    @classmethod
    def fromdate(cls, date):
        return cls.fromtimestamp(date.timestamp())

    @classmethod
    def fromabslot(cls, abslot):
        return cls.fromtimestamp(abslot*60*SlotDate.slot_size)

    @classmethod
    def fromtimestamp(cls, ts):
        date = datetime.fromtimestamp(ts)
        delta = (date-datetime(1970,1,1))
        minutes = delta.seconds // 60 
        return cls(delta.days, minutes)

    @classmethod
    def now(cls):
        now = datetime.now()
        return cls.fromdate(now)

    def __int__(self):
        return self.abslot

    def __str__(self):
        return str(self.to_date())

    def to_date(self):
        return datetime(1970,1,1) + timedelta(days=self.days, minutes=self.minutes)


class SlotTask:

    default_duration = 30 // SlotDate.slot_size

    def __init__(self, task):

        self.label = task.label

        if task.duration:
            duration = task.duration.total_seconds()
            duration /= 60*SlotDate.slot_size
        else:
            duration = SlotTask.default_duration
        self.duration = ceil(duration)
        
        if task.preftime:
            pref_start = SlotDate.fromdate(task.preftime.start)
            pref_end = SlotDate.fromdate(task.preftime.end)
            self.preftime = SlotIntervall(pref_start, pref_end)
        else:
            self.preftime = None

        if task.deadline:
            self.deadline = SlotDate.fromdate(task.deadline)
        else:
            self.deadline = None # maybe float(inf)

        if task.termin:
            self.termin = SlotDate.fromdate(task.termin)
        else:
            self.termin = None

        self.priority = task.priority

    @property
    def urgency(self, schedule_time=None):

        if not schedule_time:
            if self.schedule_time:
                schedule_time = self.schedule_time
            else :
                schedule_time = DayMinuteDate.now()

        if self.deadline:
            days_left = self.deadline.day - schedule_time.day
            minutes_left = self.deadline.minute - schedule_time.minute
            minutes_to_dead += minutes_left + days_left*work_range
      
            if self.duration:
                dur = self.duration
            else:
                dur = default_duration

            urg = timescaler / (minutes_to_dead - dur) + 1

        else:
            urg = 1
        
        return self.priority*urg

    def __str__(self):
        out = (
            ('Task',),
            ('label', self.label),
            ('deadline', self.deadline),
            ('duration', self.duration),
            ('preftime', self.preftime),
            ('priority', self.priority),
            ('termin', self.termin),
        )
        return '\n  '.join([' : '.join([str(r) for r in row]) for row in out])


class SlotIntervall:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.days = end.days - start.days
        self.slots = end.abslot - start.abslot

    def __contains__(self, abs_slot):
        return NotImplemented

    def __and__(self, sd_interv):
        return NotImplemented

    @classmethod
    def span(cls, slotdate, slots):
        if isinstance(slotdate, SlotDate):
            abslot = slotdate.abslot
        else:
            abslot = slotdate
            slotdate = SlotDate.fromabslot(abslot)
        end = SlotDate.fromabslot(abslot + slots)
        return cls(slotdate, end)
        

    def count_overlap(self, interv):
        return count_overlap(
            s1=self.start.abslot,
            e1=self.end.abslot,
            s2=interv.start.abslot,
            e2=interv.end.abslot)

    def __and__(self, interv):
        return overlap(
            s1=self.start.abslot,
            e1=self.end.abslot,
            s2=interv.start.abslot,
            e2=interv.end.abslot)

    def __str__(self):
        return ' -- '.join([str(self.start), str(self.end)])


def count_overlap(s1,e1,s2,e2):
    """ Count overlapping slots.

    >>> count_overlap(1,3,5,9)
    0
    >>> count_overlap(1,5,3,9)
    2
    >>> count_overlap(3,9,1,5)
    2
    >>> count_overlap(5,9,1,3)
    0
    >>> count_overlap(1,4,4,9)
    0
    >>> count_overlap(1,9,3,5)
    2
    >>> count_overlap(3,5,1,9)
    2
    >>> count_overlap(4,9,1,4)
    0
    >>> count_overlap(4,7,4,7)
    3
    """

    if s1 < s2:
        if e1 < s2:
            return 0
        elif e2 < e1:
            return e2-s2
        return e1-s2
    else:
        if e2 < s1:
            return 0
        elif e1 < e2:
            return e1-s1
        return e2-s1


def overlap(s1,e1,s2,e2):
    """ Gets start and enpoints of two intervalls and returns the overlapping intervall.

    >>> overlap(1,3,5,9)
    ()
    >>> overlap(1,5,3,9)
    (3, 5)
    >>> overlap(3,9,1,5)
    (3, 5)
    >>> overlap(5,9,1,3)
    ()
    >>> overlap(1,4,4,9)
    (4, 4)
    >>> overlap(1,9,3,5)
    (3, 5)
    >>> overlap(3,5,1,9)
    (3, 5)
    >>> overlap(4,9,1,4)
    (4, 4)
    >>> overlap(4,7,4,7)
    (4, 7)
    """

    if s1 > s2:
        s1,e1,s2,e2 = s2,e2,s1,e1
  
    if e1 < s2:
        return ()
    elif e2 < e1:
        return (s2,e2)

    return (s2,e1)


if __name__ == "__main__":
    ...
