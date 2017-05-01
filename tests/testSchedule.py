import unittest
import mock
import schedule
from schedule import *
from mock import patch


class TestSchedule(unittest.TestCase):
    """
    Unit tests for the Schedule class. 

    Example:
        $ ./runallTests.sh

    https://docs.python.org/2/library/unittest.html
    """

    def setUp(self):
        self.schedule_dictionary = {1: {NORMAL_HOURS_KEY: ['2', '3']},
                                    4: {NORMAL_HOURS_KEY: ['8', '20'], PEAK_HOURS_KEY: ['11', '14']},
                                    5: {NORMAL_HOURS_KEY: ['6', '7'], PEAK_HOURS_KEY: ['8', '9']}}

    def tearDown(self):
        self.schedule_dictionary = None

    def test_bad_input(self):

        o, c, ps, pe, m = getScheduleForDay(self.schedule_dictionary, 11)
        self.assertEqual(o, None)
        self.assertEqual(c, None)
        self.assertEqual(ps, None)
        self.assertEqual(pe, None)

    def test_badKey(self):

        o, c, ps, pe, m = getScheduleForDay(self.schedule_dictionary, 3)
        self.assertEqual(o, None)
        self.assertEqual(c, None)
        self.assertEqual(ps, None)
        self.assertEqual(pe, None)

    def test_expectedOutput(self):

        o, c, ps, pe, m = getScheduleForDay(self.schedule_dictionary, 5)
        self.assertEqual(o, '6')
        self.assertEqual(c, '7')
        self.assertEqual(ps, '8')
        self.assertEqual(pe, '9')

        o, c, ps, pe, m = getScheduleForDay(self.schedule_dictionary, 4)
        self.assertEqual(o, '8')
        self.assertEqual(c, '20')
        self.assertEqual(ps, '11')
        self.assertEqual(pe, '14')

        o, c, ps, pe, m = getScheduleForDay(self.schedule_dictionary, 1)

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

        # hammer bounds
        for _i in xrange(0, 1000):

            delay = calculateScheduleDelay(False)
            delay = delay / 60
            self.assertTrue(schedule.NORMAL_MIN_PERIOD_MINUTES <= delay
                            <= schedule.NORMAL_MAX_PERIOD_MINUTES)

            delay = calculateScheduleDelay(True)
            delay = delay / 60
            self.assertTrue(schedule.PEAK_MIN_PERIOD_MINUTES <= delay
                            <= schedule.PEAK_MAX_PERIOD_MINUTES)

    def test_getSecondsUntilNextDay(self):

        with patch('schedule.getCurrentDayHourMinute') as mock_getCurrentDayHourMinute:
            mock_getCurrentDayHourMinute.return_value = (4, 2, 0)
            seconds = getSecondsUntilNextDay()
            self.assertEqual(22 * 60 * 60, seconds)

            mock_getCurrentDayHourMinute.return_value = (4, 6, 30)
            seconds = getSecondsUntilNextDay()
            self.assertEqual(17 * 60 * 60 + 30 * 60, seconds)

            mock_getCurrentDayHourMinute.return_value = (4, 14, 0)
            seconds = getSecondsUntilNextDay()
            self.assertEqual(10 * 60 * 60, seconds)

    def test_isCurrentlyScheduleable(self):

        with patch('schedule.getCurrentDayHourMinute') as mock_getCurrentDayHourMinute:
            mock_getCurrentDayHourMinute.return_value = (4, 2, 0)
            self.assertFalse(isCurrentlyScheduleable(
                self.schedule_dictionary, 4))

            mock_getCurrentDayHourMinute.return_value = (4, 9, 0)
            self.assertTrue(isCurrentlyScheduleable(
                self.schedule_dictionary, 4))

            mock_getCurrentDayHourMinute.return_value = (4, 11, 30)
            self.assertTrue(isCurrentlyScheduleable(
                self.schedule_dictionary, 4))

            mock_getCurrentDayHourMinute.return_value = (4, 16, 45)
            self.assertTrue(isCurrentlyScheduleable(
                self.schedule_dictionary, 4))

            mock_getCurrentDayHourMinute.return_value = (4, 20, 0)
            self.assertFalse(isCurrentlyScheduleable(
                self.schedule_dictionary, 4))

            mock_getCurrentDayHourMinute.return_value = (4, 22, 0)
            self.assertFalse(isCurrentlyScheduleable(
                self.schedule_dictionary, 4))


if __name__ == '__main__':

    unittest.main()
