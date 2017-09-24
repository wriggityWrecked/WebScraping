import json
import logging
import time
import traceback
import sys
import os
import threading
import datetime

from datetime import timedelta
from enum import Enum
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner

from utils import get_random_user_agent
from utils.compare_tools import compare_inventory_files, dprint
from utils.slackTools import postResultsToSlackChannel, postResultsToSlackChannelWithLink
from utils.slack_tools import post_message

DEBUG_SLACK_CHANNEL = 'robot_comms'


class ScraperStage(Enum):
    """
    Enum denoting the current scraper stage. 
    """
    CREATED = 1
    INITIALIZED = 2
    RUNNING = 3
    CRAWLING = 4
    FINISHED_CRAWLING = 5
    POST_CRAWL = 6
    PROCESSING_RESULTS = 7
    POSTING_RESULTS = 8
    FINISHED = 9
    TERMINATED_ERROR = 10


class Scraper(object):

    'Base class for all scrapers'

    def __init__(self, name, spider, product_link, slack_channel):

        self.stage_lock = threading.Lock()
        self.stage = ScraperStage.CREATED

        # name of the scraper
        self.name = name

        # spider object
        self.spider = spider

        # link to use to append to an ID, todo need to make a rich object as links are page specific
        # either specify or leave blank
        self.product_link = product_link

        # slack channel name used to post results
        self.slack_channel = slack_channel

        # base directory of scraper results
        self.base_directory = os.path.join(
            os.path.dirname(__file__), 'data/' + name)

        self.start_time = 0

        self.run_event = threading.Event()
        self.queue_event = threading.Event()


    def initialize(self):

        self.setStage(ScraperStage.INITIALIZED)
        self.start_time = 0
        now = datetime.datetime.now()
        now_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        # archive directory of scraper results
        self.archive_directory = self.base_directory + \
            '/' + now.strftime("%Y-%m")

        # file name to dump Spider JSON output
        # timestamp in case of failures
        self.new_file_name = self.base_directory + '/' + 'new_' + \
            self.name + 'Result_' + now_string + '.json'

        # file name to keep as inventory file: used for all new vs old
        # comparisons
        self.inventory_file_name = self.base_directory + \
            '/' + self.name + 'BeerInventory.json'

        # file name for comparison results
        self.results_output_file_name = self.archive_directory + '/' + \
            'results_' + self.name + 'Beer'  # append time and .json later

        # file name for old inventory data
        self.rotated_file_name = self.archive_directory + '/' + \
            'old_' + self.name + '_'  # append time and .json later

        # logging directory for this scraper
        self.log_directory = self.base_directory + '/' + 'log'

        # log name each time run is called
        self.log_name = self.log_directory + '/' + self.name + '_' + now_string + '.log'

        self.checkAndSetupDirectories(self.base_directory, self.archive_directory, self.log_directory)

        # set logger name
        self.logger = logging.getLogger(__name__)

        # set format
        logging.basicConfig(filename=self.log_name, filemode='w', level=logging.INFO,
                            format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        self.logger.setLevel(logging.DEBUG)


    def setStage(self, newStage):

        with self.stage_lock:
            print 'setting stage to ' + str(newStage)
            self.stage = newStage


    def __str__(self):

        string = "Stage=" + str(self.stage)

        if self.start_time != 0:

            if self.stage == ScraperStage.FINISHED:
                string += ", Finished "
            else:
                string += ", Started "

            string += str(timedelta(seconds=(time.time() -
                                             self.start_time))) + " ago."

        return string


    def checkAndSetupDirectories(self, base_directory, archive_directory, log_directory):

        # housekeeping for files storage, e.g.
        # named directory for results
        if not os.path.isdir(base_directory):
            logging.info('creating ' + base_directory)
            os.makedirs(base_directory)

        if not os.path.isdir(self.archive_directory):
            logging.info('creating ' + self.archive_directory)
            os.makedirs(self.archive_directory)

        if not os.path.isdir(log_directory):
            logging.info('creating ' + log_directory)
            os.makedirs(log_directory)

        # check if a results file exists (it shouldn't if properly rotated)
        # shouldn't be possible now with timestamp
        if os.path.isfile(self.new_file_name):
            logging.warn(self.new_file_name + ' + already exists!')


    def runSpider(self, one_shot):
        """
        Rather than using scrapyd or executing the spider manually via scrapy,
        this method creates a CrawlerRunnerand runs the spider provided at
        construction. 

        https://doc.scrapy.org/en/latest/topics/practices.html#run-from-script
        http://twistedmatrix.com/trac/wiki/FrequentlyAskedQuestions#Igetexceptions.ValueError:signalonlyworksinmainthreadwhenItrytorunmyTwistedprogramWhatswrong
        """
        try:

            while True:

                self.setStage(ScraperStage.CRAWLING)
                self.start_time = time.time()
                self.run_event.clear()

                # post debug message to slack
                post_message(DEBUG_SLACK_CHANNEL, 'Starting scraper ' + self.name)

                #configure_logging( {'LOG_FORMAT': '%(levelname)s: %(message)s'} )
                runner = CrawlerRunner({
                    'USER_AGENT': get_random_user_agent.get_random_user_agent(),
                    'FEED_FORMAT': 'json',
                    'FEED_URI': self.new_file_name,
                    'AUTOTHROTTLE_ENABLED': 'True',
                    'DUPEFILTER_DEBUG': 'True'
                })

                #todo deferred spider or something like
                #https://kirankoduru.github.io/python/multiple-scrapy-spiders.html
                _d = runner.crawl(self.spider)

                if one_shot:
                    self.logger.info('ONESHOT')
                    # stop the reactor when we're done
                    _d.addBoth(lambda _: reactor.stop())
                    reactor.run()  # this will block until stop is called
                else:
                    self.logger.info('run continuous')
                    # add a callback when we're finished
                    _d.addBoth(lambda _: self.post_crawl_continuous())
                    # todo someone else needs to handle this!
                    if not reactor.running:
                        print 'starting reactor'
                        _t = threading.Thread(target=reactor.run, kwargs={
                                         'installSignalHandlers': 0}).start()
                    else:
                        print 'reactor already running'

                    print 'waiting for event....'
                    self.run_event.wait() #block until run is done with the first
                    print 'event fired, done with a crawler'
                    self.run_event.clear()

                #todo don't return here, just fire an event that we are done
                return True, None

        except KeyboardInterrupt:
            raise KeyboardInterrupt("KeyboardInterrupt caught in runSpider")
        except Exception as _e:
            exc_type, exc_value, exec_tb = sys.exc_info()
            return False, 'Caught ' \
                + str("".join(traceback.format_exception(exc_type, exc_value, exec_tb)))


    def processSpiderResults(self):
        """
        Process / Compare new results obtained from the associated Spider in this class.
        If the inventory file does not exist, then the new file becomes our inventory.

        Otherwise, use the module compare_tools to obtain our added and removed
        items from inventory.
        """

        try:
            self.setStage(ScraperStage.PROCESSING_RESULTS)

            # Crawling must be successful or the new file and inventory files
            # must exist as this point
            if not os.path.isfile(self.new_file_name):

                reason = str(self.new_file_name) + ' not found!'
                logging.warning((reason))

                return False, reason

            if not os.path.isfile(self.inventory_file_name):
                reason = str(self.inventory_file_name) + ' not found!' + \
                    ', saving ' + self.new_file_name + ' as ' + self.inventory_file_name

                logging.info(reason)
                os.rename(self.new_file_name, self.inventory_file_name)

                return False, reason

            # Both files exist, OK to compare
            logging.debug(
                'compare_inventory_files( ' + self.inventory_file_name + ", "\
                     + self.new_file_name + " )")
            removed, added = compare_inventory_files(
                self.inventory_file_name, self.new_file_name)

            # debug printing
            dprint(removed, added)

            # now we have a new inventory file, rotating to inventory_file_name
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            self.rotated_file_name = self.rotated_file_name + now + '.json'

            logging.debug('rotating ' + self.inventory_file_name +
                          ' to ' + self.rotated_file_name)

            os.rename(self.inventory_file_name, self.rotated_file_name)
            os.rename(self.new_file_name, self.inventory_file_name)

            # compile results
            results = {}
            results['addedLength'] = len(added)
            results['addedList'] = added
            results['removedLength'] = len(removed)
            results['removedList'] = removed

            logging.debug('results = ' + str(results))

            # save results
            self.results_output_file_name = self.results_output_file_name + '_'\
                 + now + '.json'
            with open(self.results_output_file_name, 'w') as out_file:
                logging.debug('saving ' + self.results_output_file_name)
                json.dump(results, out_file)

            return True, results

        except Exception as _e:
            exc_type, exc_value, exec_tb = sys.exc_info()
            return False, 'Caught ' \
                + str("".join(traceback.format_exception(exc_type, exc_value, exec_tb)))


    def postToSlack(self, results, slack_channel):
        """
        Construct a results string, from the input, and post to the input Slack channel.
        """

        try:

            self.setStage(ScraperStage.POSTING_RESULTS)

            # post to slack
            if not self.product_link:
                postResultsToSlackChannel(results, slack_channel)
            else:
                postResultsToSlackChannelWithLink(
                    results, self.product_link, slack_channel)

            added_removed = 'Added: ' + str(results['addedLength']) + \
                ', Removed: ' + str(results['removedLength'])
            # post to debug slack
            post_message(DEBUG_SLACK_CHANNEL, 'Finished crawler ' + self.name \
                + ', ' + added_removed + ', time taken = '\
                + str(timedelta(seconds=(time.time() - self.start_time))))

            return True, None

        except Exception:
            exc_type, exc_value, exec_tb = sys.exc_info()
            return False, 'Caught ' \
                + str("".join(traceback.format_exception(exc_type, exc_value, exec_tb)))


    def reportErrorsToSlack(self, error_message):

        try:

            post_message(DEBUG_SLACK_CHANNEL, error_message)
            return True, None

        except Exception:
            exc_type, exc_value, exec_tb = sys.exc_info()
            return False, 'Caught ' \
                + str("".join(traceback.format_exception(exc_type, exc_value, exec_tb)))


    def postCrawl(self):
        try:
            self.setStage(ScraperStage.POST_CRAWL)

            # Now attempt to obtain results
            success, results = self.processSpiderResults()

            if not success:
                error_message = 'processSpiderResults failed\n' + results
                self.logger.error(error_message)
                self.reportErrorsToSlack(error_message)
                self.setStage(ScraperStage.TERMINATED_ERROR)
                return False, error_message

            # post the results to slack
            success, message = self.postToSlack(results, self.slack_channel)

            if not success:
                self.logger.error('postToSlack failed\n' + message)
                #self.setStage( ScraperStage.TERMINATED_ERROR )
                # return False, error_message

            return True, results

        finally:
            print 'setting run_event'
            self.run_event.set()

    def post_crawl_continuous(self):
        print 'post_crawl_continuous'
        self.postCrawl()
        print 'done post crawl, waiting for queue event'
        self.queue_event.wait()
        print 'finished waiting post crawl cont'
        self.queue_event.clear()
        self.run()

    def start_new_job(self):
        print 'starting new job yo'
        self.queue_event.set()

    def run(self):
        """
        Main workhorse method of the class. It creates and runs the spider, 
        new file output to stored inventory,
        processes and saves results, and then posts to the appropriate Slack 
        channel. 

        This does not block!

        TODO this should be removed / deprecated 
        """
        self.initialize()
        self.setStage(ScraperStage.RUNNING)

        success, message = self.runSpider(False)
        # this will callback

        if not success:
            error_message = 'runSpider failed\n' + message
            self.logger.error(error_message)
            self.reportErrorsToSlack(error_message)
            self.setStage(ScraperStage.TERMINATED_ERROR)
            #return False, error_message

        return True, message


    def one_shot(self):
        """ Blocking run. AKA ONESHOT

        TODO rename as run
        """
        self.initialize()
        self.setStage(ScraperStage.RUNNING)

        success, message = self.runSpider(True)

        if not success:
            error_message = 'runSpider failed\n' + message
            self.logger.error(error_message)
            self.reportErrorsToSlack(error_message)
            self.setStage(ScraperStage.TERMINATED_ERROR)
            return False, error_message

        success, message = self.postCrawl()

        self.setStage(ScraperStage.FINISHED)
        return True, message
