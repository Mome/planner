import schedule
from task import Task
import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta as td
import numpy as np
from itertools import accumulate
from functools import partial

plot_wtf = False
plot_urgfunc = False
plot_cwta = False
plot_timefit = 1
plot_task_fitness = 1
plot_urgency = 1


# create worktime function
wtf = schedule.get_linear_wtf(
    start_slot=8*12,
    end_slot=18*12,
    tolerance=2*12,
    baseline=0.1,
)

if plot_wtf:
    x = range(0,24*12)
    y = list(map(wtf, x))
    in_hours = (24*12)//12
    plt.figure()
    plt.locator_params(nbins=20)
    plt.axis([0, in_hours, 0, 1.1])
    plt.plot(np.linspace(0,in_hours,24*12), y)
    plt.title('wtf')
    plt.grid(True)


# create urgency function
euf = schedule.get_exponential_urgfunc(
    max_urg=10,
    urg_influence=1,
)

huf = schedule.get_harmonic_urgfunc(
    max_urg=10,
    decay=0.001,
)

uf = huf

if plot_urgfunc:
    x = range(-1,200*12)
    y = list(map(uf, x))
    #in_hours = (24*12)//12
    plt.figure()
    plt.locator_params(nbins=20)
    #plt.axis([x[0], x[-1], 0, max(y)+0.1])
    plt.plot(x, y)
    plt.title('urgfunc')
    plt.grid(True)

# create task fittness function
task_fitness = schedule.get_task_fittness(
    worktime_func = wtf,
    urgency_func = uf,
    preftime_weight = 0.7,
    early_bonus_decay = 0.001,
    max_early_bonus = 0.5,
)

tasks = [
    Task('wasser trinken'),
    Task('hausarbeit', duration={'minutes':200}),
    Task('tee trinken', deadline='2015.11.21 12:00'),
    Task('waesche holen', priority=2),
    Task('kaffee trinken', preftime='day after tomorrow'),
]

# extract the termins
termins = [t for t in tasks if t.termin]
tasks   = [t for t in tasks if not t.termin]

# convert to SlotTasks, to round the time
s_tasks = [schedule.SlotTask(t) for t in tasks]
s_termins = [t for t in tasks if t.termin]

now = schedule.SlotDate.now()
start = now.abslot - now.slot
end = schedule.SlotDate.fromdate(dt.now() + td(days=4)).abslot
print('start:', start, ' end:', end)

tasks_per_day = schedule.SlotDate.slots_per_day
print('tasks_per_day', tasks_per_day)
wta = [wtf(i) for i in range(tasks_per_day)]
cwta = list(accumulate(wta))

if plot_cwta:
    plt.figure()
    plt.plot(cwta)
    plt.title('cummulative worktime')


show_tasks = [s_tasks[0],s_tasks[2]] # <-------------------------------------------------|

x = np.linspace(0, (end-start)/(60/5), end-start)
a = np.array(range(0, int((end-start)//(60/5)), 4))

if plot_timefit:
    
    tff = partial(schedule.timefit, cwta=cwta, ptw=0.7)
    
    plt.figure()
    min_val = 0.0
    max_val = -float('inf')
    for task in show_tasks:
        fitness_values = [tff(task.preftime, task.duration, i) for i in range(start, end)]    
        plt.plot(x, fitness_values)
        if min(fitness_values) < min_val:
            min_val = min(fitness_values)
        if max_val < max(fitness_values):
            max_val = max(fitness_values)

    plt.xticks(a, a%24)
    plt.axis([x[0], x[-1], min_val - 0.1, max_val + 0.15])
    plt.legend([x.label for x in show_tasks])
    plt.title('timefit')
    plt.grid()


if plot_urgency:
    
    urgency = partial(schedule.urgency, urgfunc=uf)
    
    plt.figure()
    min_val = 0.0
    max_val = -float('inf')
    for task in show_tasks:
        urg_val = [urgency(task, i) for i in range(start, end)] 
        plt.plot(x, urg_val)
        if task.deadline:
            plt.axvline((task.deadline.abslot-start)/(60/5), color='red')
            print('deadline', task.deadline.abslot)
        if min(urg_val) < min_val:
            min_val = min(urg_val)
        if max_val < max(urg_val):
            max_val = max(urg_val)

    plt.xticks(a, a%24)
    plt.axis([x[0], x[-1], min_val - 0.1, max_val + 0.15])
    plt.legend([x.label for x in show_tasks])
    plt.title('urgency')
    plt.grid()


if plot_task_fitness:

    plt.figure()
    min_val = 0.0
    max_val = -float('inf')
    for task in show_tasks:
        fitness_values = [task_fitness(task, i) for i in range(start, end)]    
        plt.plot(x, fitness_values)
        if min(fitness_values) < min_val:
            min_val = min(fitness_values)
        if max_val < max(fitness_values):
            max_val = max(fitness_values)

    plt.xticks(a, a%24)
    plt.axis([x[0], x[-1], min_val - 0.1, max_val + 0.15])
    plt.legend([x.label for x in show_tasks])
    plt.title('task_fittness')
    plt.grid()

for t in show_tasks:
    print(t)

plt.show()