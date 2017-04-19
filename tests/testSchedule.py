import unittest
import mock
import schedule
from schedule import *
from mock import *

class TestSchedule(unittest.TestCase):
    """
    Unit tests for the Schedule class. 
    """
    def setUp(self):
        self.scheduleDictionary = {1: {NORMAL_HOURS_KEY: ['2', '3']}, \
                                5: {NORMAL_HOURS_KEY: ['6', '7'], PEAK_HOURS_KEY: ['8', '9']}}

    def test_badInput(self):

        o, c, ps, pe, m = getScheduleForDay(self.scheduleDictionary, 11)
        self.assertEqual(o, None)
        self.assertEqual(c, None)
        self.assertEqual(ps, None)
        self.assertEqual(pe, None)

    def test_badKey(self):

        o, c, ps, pe, m = getScheduleForDay(self.scheduleDictionary, 4)
        self.assertEqual(o, None)
        self.assertEqual(c, None)
        self.assertEqual(ps, None)
        self.assertEqual(pe, None)

    def test_expectedOutput(self):

        o, c, ps, pe, m = getScheduleForDay(self.scheduleDictionary, 5)
        self.assertEqual(o, '6')
        self.assertEqual(c, '7')
        self.assertEqual(ps, '8')
        self.assertEqual(pe, '9')

        o, c, ps, pe, m = getScheduleForDay(self.scheduleDictionary, 1)

        self.assertEqual(o, '2')
        self.assertEqual(c, '3')
        self.assertEqual(ps, None)
        self.assertEqual(pe, None)

    def test_getMinutesFromStringEntry(self):

        m = getMinutesFromStringEntry('1:2')
        self.assertEqual(62, m)

        m = getMinutesFromStringEntry('1')
        self.assertEqual(60, m)

        m = getMinutesFromStringEntry('')
        self.assertEqual(None, m)

    def test_calculateScheduleDelay(self):
        #hammer bounds
        for i in xrange(0,100):

            with patch('schedule.getCurrentDayHourMinute') as mock_getCurrentDayHourMinute:

                mock_getCurrentDayHourMinute.return_value = (4,2,6)
                delay = calculateScheduleDelay(1*60, 3*60) / 60
                self.assertNotEqual(-1, delay)
                self.assertTrue( schedule.OPEN_MIN_PERIOD_MINUTES  <= delay \
                                <= schedule.OPEN_MAX_PERIOD_MINUTES  )

if __name__ == '__main__':

    unittest.main()
