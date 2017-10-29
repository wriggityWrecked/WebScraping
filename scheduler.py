import threading
import time
import datetime
import signal
from multiprocessing import Queue, Process
import run_scraper

from enum import Enum
from schedule import *
from utils.slack_tools import post_message, SlackPost

DEBUG_SLACK_CHANNEL = 'robot_comms' #todo move to slack_tools module


class SchedulerStage(Enum):

    CREATED = 1
    WAITING = 2
    DELAYING = 3
    RUNNING = 4
    EXECUTING = 5
    TERMINATED = 6

class Scheduler(object):

    def __init__(self, name, schedule_dictionary, module_name, multiprocessing_queue):

        #todo assertions for not None?

        self.schedule_dictionary = schedule_dictionary
        self.time_last_ran = 0
        self.number_of_times_run = 0
        self.number_of_times_waited = 0
        self.event = threading.Event()
        self.event_lock = threading.RLock()
        self.name = name
        self.stage = SchedulerStage.CREATED
        self.module_name = module_name
        self.multiprocessing_queue = multiprocessing_queue
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

    #todo need a stop method

    def start_scraper_process(self):

        #launch a sub process, because the twisted reactor
        #won't accept new jobs after run is called
        
        #todo new thread and monitor if need be
        self.stage = SchedulerStage.EXECUTING
        print self

        #using another process because the twisted reactor cannot be restarted
        module_target = getattr(run_scraper, self.module_name)
        _p = Process(target=module_target, args=(), kwargs={'multiprocessing_queue':self.multiprocessing_queue}) #todo pass the multiprocessing queue as an arg
        _p.start()
        _p.join()        

        #todo this should be a blocking call, e.g. one shot
        self.number_of_times_run += 1
        #todo time this
        self.stage = SchedulerStage.RUNNING

    def run(self):

        #post message needs to be queued
        post_message(DEBUG_SLACK_CHANNEL, "starting schedule for " + self.name)
        self.stage = SchedulerStage.RUNNING

        while not self._is_event_lock_set():

            #todo first case, run it right away if time to do so, otherwise wait

            if self.number_of_times_run == 0:
                print 'running first scraper'
                self.start_scraper_process()
                post_message(DEBUG_SLACK_CHANNEL, str(self))


            print self
            print 'run'
            self.time_last_ran = datetime.datetime.now()

            day, _, _ = getCurrentDayHourMinute()
            delay_seconds = getScheduleDelayForDay(self.schedule_dictionary, day)
            print 'delay_seconds=' + str(delay_seconds)

            _run_scraper = True if delay_seconds != -1 else False

            if _run_scraper:
                self.stage = SchedulerStage.WAITING
                msg = self.name + 'waiting ' + str(datetime.timedelta(\
                    seconds=delay_seconds)) + ' to run scraper'
                print msg
                post_message(DEBUG_SLACK_CHANNEL, msg)
            else:

                #DON"T SLEEP: https://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3

                self.stage = SchedulerStage.DELAYING
                delay_seconds = getSecondsUntilNextDay()
                msg = self.name + 'waiting ' + str(datetime.timedelta(\
                    seconds=delay_seconds)) + ' until next day'
                print msg
                post_message(DEBUG_SLACK_CHANNEL, msg)

            self.number_of_times_waited += 1
            self.event.wait(timeout=delay_seconds)

            if self._is_event_lock_set():
                self.stage = SchedulerStage.TERMINATED
                print self
                msg = self.name + 'exiting run' + ' ' + str(self)
                post_message(DEBUG_SLACK_CHANNEL, msg)
                return

            if _run_scraper:
                self.start_scraper_process()

            print self
            post_message(DEBUG_SLACK_CHANNEL, str(self))

        print 'no run'

def schedule_knl():

    q = Queue()

    ##todo try catch for KeyBoard
    sd = {0: {NORMAL_HOURS_KEY: ['9', '21'], PEAK_HOURS_KEY: ['10', '15']},\
            1: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10', '15']},\
            2: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10', '15']},\
            3: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10', '15']},\
            4: {NORMAL_HOURS_KEY: ['9', '20'], PEAK_HOURS_KEY: ['10', '15']},\
            5: {NORMAL_HOURS_KEY: ['8', '20']},\
            6: {NORMAL_HOURS_KEY: ['9', '20']}}

    test = Scheduler('knl', sd, 'knl_spirits', q) #todo needs input queue
    t = threading.Thread( target=test.run, args=())

    #todo a scheduler should handle this thread
    try:
        t.start()
        while t.isAlive(): 

            p = q.get() #slackPost
            post_message(p.channel, p.message)

            t.join(1) #todo longer wait?
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
        #http://stackoverflow.com/questions/29100568/how-can-i-stop-python
        #-script-without-killing-it

def schedule_etre():

    ##todo try catch for KeyBoard
    sd = {0: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            1: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            2: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            3: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            4: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            5: {NORMAL_HOURS_KEY: ['0', '10']},\
            6: {NORMAL_HOURS_KEY: ['0', '10']}}

    test = Scheduler('etre', sd, 'scrape_etre.py')
    t = threading.Thread( target=test.run, args=() )

    try:
        t.start()
        while t.isAlive(): 
            t.join(120) #todo longer wait?
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
        #http://stackoverflow.com/questions/29100568/how-can-i-stop-python
        #-script-without-killing-it

def schedule_bh():

    ##todo try catch for KeyBoard
    sd = {0: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            1: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            2: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            3: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            4: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
            5: {NORMAL_HOURS_KEY: ['0', '10']},\
            6: {NORMAL_HOURS_KEY: ['0', '10']}}

    test = Scheduler('belgian_happiness', sd, 'scrape_belgian_happiness.py')
    t = threading.Thread( target=test.run, args=() )

    try:
        t.start()
        while t.isAlive():



            t.join(1) #todo longer wait?
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
        #http://stackoverflow.com/questions/29100568/how-can-i-stop-python
        #-script-without-killing-it

def startProcesses():
    print 'hi'
    #todo

    #construct a shared multiprocessing queue

    #start KnL process as daemon
    #start Etre as daemon

    #handle the queue entries as a non-daemon, we only care about
    #scraping and posting results until the end of time


if __name__ == "__main__":

    schedule_knl()

    # if len( sys.argv ) > 1:
    #     script_name = sys.argv[1]

    #     if 'etre' in script_name:
    #         schedule_etre()
    #     elif 'knl' in script_name:
    #         schedule_knl()
    #     elif 'bh' in script_name:
    #         schedule_bh()
    #     else:
    #         print 'invalid input'
