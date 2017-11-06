import threading
import time
import datetime
import signal
from multiprocessing import Queue, Process
from enum import Enum
from random import uniform

import run_scraper
from utils.schedule_utils import is_currently_schedulable, get_seconds_until_next_day
from utils.slack_tools import post_message, post_message_to_queue, SlackPost, DEBUG_SLACK_CHANNEL


class SchedulerStage(Enum):

    CREATED = 1
    WAITING = 2
    DELAYING = 3
    RUNNING = 4
    EXECUTING = 5
    TERMINATED = 6

class Scheduler(object):

    def __init__(self, name, start_time_hour, end_time_hour, module_name, multiprocessing_queue, min_wait_seconds=60, max_wait_seconds=30*60):

        #todo assertions for start_time < end_time
        self.name = name

        self.start_time_hour = start_time_hour
        self.end_time_hour = end_time_hour
        self.module_name = module_name
        self.multiprocessing_queue = multiprocessing_queue
        self.min_wait_seconds = min_wait_seconds
        self.max_wait_seconds = max_wait_seconds

        self.time_last_ran = 0
        self.number_of_times_run = 0
        self.number_of_times_waited = 0

        self.event = threading.Event() #todo private
        self.event_lock = threading.RLock() #todo private
        self.stage = SchedulerStage.CREATED #todo private


    def __str__(self):

        time_string = '' if self.time_last_ran == 0 else ', time_last_ran=' \
                        + self.time_last_ran.strftime("%Y-%m-%dT%H:%M:%S")

        return 'stage=' + str(self.stage) \
            + time_string \
            + ', number_of_times_run=' \
            + str(self.number_of_times_run) + ', number_of_times_waited=' \
            + str(self.number_of_times_waited)


    def set_event_lock(self, set_):
        """
        When set it kills this scheduler, but doesn't interrupt a task in progress
        """
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
        _p = Process(target=module_target, args=(), kwargs={'multiprocessing_queue':self.multiprocessing_queue, 'debug_flag':True}) 
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

            _run_scraper = is_currently_schedulable(self.start_time_hour, self.end_time_hour)
            delay_seconds = None #init

            if _run_scraper:
                self.stage = SchedulerStage.WAITING

                #get a random time to wait
                #guassian distro?
                delay_seconds = uniform(self.min_wait_seconds, self.max_wait_seconds)

                msg = self.name + 'waiting ' + str(datetime.timedelta(\
                    seconds=delay_seconds)) + ' to run scraper'
                print msg
                post_message(DEBUG_SLACK_CHANNEL, msg)

            else:
                self.stage = SchedulerStage.DELAYING

                #todo? https://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3

                delay_seconds = get_seconds_until_next_day()
                msg = self.name + 'waiting ' + str(datetime.timedelta(\
                    seconds=delay_seconds)) + ' until next day'
                print msg
                post_message(DEBUG_SLACK_CHANNEL, msg)

            self.number_of_times_waited += 1
            self.event.wait(timeout=delay_seconds)

            if self._is_event_lock_set():
                self.stage = SchedulerStage.TERMINATED
                print self
                msg = self.name + ' exiting run' + ' ' + str(self)
                post_message(DEBUG_SLACK_CHANNEL, msg)
                return

            if _run_scraper:
                print('_run_scraper='+str(_run_scraper))
                self.start_scraper_process()

            print self
            post_message(DEBUG_SLACK_CHANNEL, str(self))

        print 'no run'

def schedule_knl():

    #todo start and end time


    q = Queue()

    test = Scheduler('knl', 8, 20, 'knl_beer', q, min_wait_seconds=2*60, max_wait_seconds=12*60)
    t = threading.Thread( target=test.run, args=())

    #todo a scheduler should handle this thread
    try:
        t.start()
        while t.isAlive(): 

            p = q.get() #slackPost
            print("draining queue "+ str(p))
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

# def schedule_etre():

#     #todo start and end time


#     ##todo try catch for KeyBoard
#     sd = {0: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             1: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             2: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             3: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             4: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             5: {NORMAL_HOURS_KEY: ['0', '10']},\
#             6: {NORMAL_HOURS_KEY: ['0', '10']}}

# def schedule_bh():

#     #todo start and end time

#     ##todo try catch for KeyBoard
#     sd = {0: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             1: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             2: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             3: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             4: {NORMAL_HOURS_KEY: ['0', '10'], PEAK_HOURS_KEY: ['2', '6']},\
#             5: {NORMAL_HOURS_KEY: ['0', '10']},\
#             6: {NORMAL_HOURS_KEY: ['0', '10']}}

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
