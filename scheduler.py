import threading
import time
import datetime
import signal
import subprocess

from enum import Enum
from schedule import *
from spiders.knl_spider import KnLBeerSpider
from scraper import *
from utils.slackTools import postMessage


class SchedulerStage(Enum):

    CREATED = 1
    WAITING = 2
    RUNNING = 3
    TERMINATED = 4

class Scheduler(object):

    def __init__(self, Scraper, schedule_dictionary):

        self.schedule_dictionary = schedule_dictionary
        self.scraper = Scraper
        self.events = {}
        self.time_last_ran = 0
        self.number_of_times_run = 0
        self.number_of_times_waited = 0
        self.event = threading.Event()
        self.event_lock = threading.RLock()
        self.stage = SchedulerStage.CREATED
        # todo validate input dictionary

    def __str__(self):

        time_string = '' if self.time_last_ran == 0 else ', time_last_ran=' \
                        + self.time_last_ran.strftime("%Y-%m-%dT%H:%M:%S")

        return 'stage=' + str(self.stage) \
            + time_string \
            + ', number_of_times_run=' \
            + str(self.number_of_times_run) + ', number_of_times_waited=' \
            + str(self.number_of_times_waited)


    def set_event_lock(self, set_):

        with self.event_lock:
            if set_:
                self.event.set()
            else:
                self.event.clear()


    def _is_event_lock_set(self):

        with self.event_lock:
            return self.event.isSet()


    def run_scraper(self):

        #todo launch a stupid fucking sub process, because the twisted reactor
        #won't accept new jobs after run is called
        subprocess.call(["python", "scrape_knl.py"])
        # self.stage = SchedulerStage.RUNNING
        # success, message = self.scraper.run()
        #can't do oneshot, it needs main thread
        #need to do background, but also wait 
        #and don't schedule on top of it
        #print message
        #return success


    def run(self):

        postMessage(DEBUG_SLACK_CHANNEL, "starting schedule for " + str(self.scraper))
        self.stage = SchedulerStage.RUNNING

        while not self._is_event_lock_set():

            #todo first case, run it right away if time to do so, otherwise wait

            if self.number_of_times_run == 0:
                print 'running first scraper'
                self.run_scraper()
                postMessage(DEBUG_SLACK_CHANNEL, str(self))
                self.number_of_times_run += 1


            print self
            print 'run'
            self.time_last_ran = datetime.datetime.now()

            day, _, _ = getCurrentDayHourMinute()
            delay_seconds = getScheduleDelayForDay(self.schedule_dictionary, day)
            print str(delay_seconds)

            _run_scraper = True if delay_seconds != -1 else False

            if _run_scraper:
                delay_seconds=5
                msg = 'waiting ' + str(datetime.timedelta(seconds=delay_seconds))+ ' to run scraper'
                print msg
                postMessage(DEBUG_SLACK_CHANNEL, msg)
            else:
                delay_seconds = getSecondsUntilNextDay()
                msg = 'waiting ' + str(datetime.timedelta(seconds=delay_seconds)) + ' until next day'
                print msg
                postMessage(DEBUG_SLACK_CHANNEL, msg)

            self.stage = SchedulerStage.WAITING
            self.number_of_times_waited += 1

            self.event.wait(timeout=delay_seconds)

            if self._is_event_lock_set():
                print 'asdfasdf'
                self.stage = SchedulerStage.TERMINATED
                print self
                print 'exiting run'
                return

            if _run_scraper:
                self.run_scraper()
                self.number_of_times_run += 1

            print self
            postMessage(DEBUG_SLACK_CHANNEL, str(self))

        print 'no run'

def main():

    knl_scraper = Scraper('knl', KnLBeerSpider,
                    'http://www.klwines.com/p/i?i=', 'knlscraper')

    ##todo try catch for KeyBoard
    sd = {0: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10:30', '15']},\
            1: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10:30', '15']},\
            2: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10:30', '15']},\
            3: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10:30', '15']},\
            4: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10:30', '15']},\
            5: {NORMAL_HOURS_KEY: ['8', '20']},\
            6: {NORMAL_HOURS_KEY: ['9', '22']}}

    test = Scheduler(knl_scraper, sd)
    t = threading.Thread( target=test.run, args=() )

    try:
        print 'hi'
        #is this needed?
        t.daemon = True
        t.start()
        while t.isAlive(): 
            t.join(60) #todo longer wait?
            print time.time()
            #todo log we are waiting and active..?
    except (KeyboardInterrupt, SystemExit):
        print 'interrupted!!'
        test.set_event_lock(True)
        print test._is_event_lock_set()
        print test
        #todo better waiting mechanism for run to fall through
        #test.join()
        print test
        print 'interrupted and done'
        #http://stackoverflow.com/questions/29100568/how-can-i-stop-python-script-without-killing-it

if __name__ == "__main__":
    main()
