from datetime import datetime, timedelta


relative_days = {'yesterday':-1, 'today':0, 'tomorrow':1}
relative_days.update({k[:3]:v for k,v in relative_days.items()})

weekday_map = {v:i for i,v in enumerate(['monday','tuesday','wednesday','thursday','friday','saturday','sunday'])}
weekday_map.update({k[:3]:k for k in weekday_map})

adverb_map = {'last':-1,'this':0,'next':1}


def parse_datetime(date_str):
    now = datetime.now()

    if not date_str:
        return now

    parameters = {}
    modifier = 0
    date_str = date_str.lower()
    for expr in filter(bool, date_str.split(' ')):
        if expr in adverb_map:
            modifier = adverb_map[expr]
            continue
        elif '.' in expr:
            if expr.endswith('.'): # allow writing like: 31.01. as well as 31.01
                expr = expr[:-1]
            expr = expr.split('.')
            assert len(expr) <= 3
            if len(expr) >= 1:
                parameters['day'] = int(expr[0])
            if len(expr) >= 2:
                parameters['month'] = int(expr[1])
            if len(expr) == 3:
                parameters['year'] = int(expr[2])
        elif ':' in expr:
            if expr.endswith(':'): # allow writing like: 12:32 as well as 32:
                expr = expr[:-1]
            expr = expr.split(':')
            assert len(expr) <= 3
            if len(expr) >= 1:
                parameters['hour'] = int(expr[0])
            if len(expr) >= 2:
                parameters['minute'] = int(expr[1])
            if len(expr) == 3:
                parameters['second'] = int(expr[2])
        else:
            if expr in weekday_map:
                dt = next_weekday(modifier, expr)
            elif expr in relative_days:
                delta = relative_days[expr]
                dt = (now + timedelta(days=delta))
            else:
                try:
                    delta = int(expr)
                    dt = (now + timedelta(days=delta))
                except ValueError:
                    pass

            if 'dt' not in locals():
                raise ParsingError('Cannot interprete ´' + str(date_str) + '´ (especially: ´' + str(expr) +  '´, type: ' + str(type(expr)) +  ') as a date.')
                
            parameters['day'] = dt.day 
            parameters['month'] = dt.month 
            parameters['year'] = dt.year
            del dt

        if 'year' not in parameters:
            parameters['year'] = now.year
        if 'month' not in parameters:
            parameters['month'] = now.month
        if 'day' not  in parameters:
            parameters['day'] = now.day
 
        # year correction to current century
        if 0 <= parameters['year'] < 100:
            parameters['year'] = (now.year // 100) * 100 + parameters['year']
       
        # 
        return datetime(**parameters)


class ParsingError(ValueError):
    pass

def next_weekday(d, weekday):
    if isinstance(weekday, str):
        weekday = weekday_map[weekday]
    if isinstance(d, int):
        d = datetime.now() - timedelta(days=d*7)
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)
if __name__ == '__main__':
    for test_str in ['1.','2','12.3.13','12.4 12:12', '12:', 'next friday', 'this monday', 'tom']:
        print(test_str, ':', parse_datetime(test_str))

#------------------------------------------
"""
from pyparsing import Word, nums, CaselessKeyword as CKWord
from functools import reduce
from operator import xor


class TimeParser:

    def __init__(self):
        date = Word(nums) + ':' + Word(nums) + ':' + Word(nums)
        date = date.setResultsName('date')
        weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        weekday = reduce(xor, [CKWord(w) for w in weekdays])
        weekday = weekday.setResultsName('weekday')
        adverbs = ['next','last','this']
        adverb = reduce(xor, [CKWord(a) for a in adverbs])
        adverb = adverb.setResultsName('adverb')
        relative_days = ['today','tomorrow','yesterday']
        rela_day = reduce(xor, [CKWord(rd) for rd in relative_days])
        rela_day = rela_day.setResultsName('relative_day')
        day = (adverb + weekday) ^ (weekday) ^ (date) ^ (rela_day)
        day = day.setResultsName('day')
 
        self.date_expr = day

    def parse_date(self, date_str):
        return self.date_expr.parseString(date_str)

tp = TimeParser()

date = tp.parse_date('this monday')

print(repr(date))"""
