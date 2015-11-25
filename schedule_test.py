import unittest

from schedule import SlotDate
from pprint import pprint


class SlotDateTest(unittest.TestCase):
    ...


class TaskFittnessTest(unittest.TestCase):
    ...


class ScheduleTest(unittest.TestCase):        

    def test_schedule(self):

        from task import Task, TaskList
        from schedule import schedule
        tasks = [
            Task('wasser trinken'),
            Task('hausarbeit', duration={'minutes':60}),
            Task('tee trinken', deadline='2015.11.24 12:00'),
            Task('waesche holen', priority=2),
            Task('kaffee trinken', preftime='day after tomorrow'),
            Task('mit lara treffen', termin='2015.11.22 12:00'),
        ]
        tasklist = TaskList()
        tasklist.add(*tasks)
        
        tasklist.schedule()

        tasklist.save('~/tasks')

        for t in tasks:
            print(t)

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()