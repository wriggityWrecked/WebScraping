"""
Wrapper class for a Scrapy spider. This class performs all the useful work after a
Scrapy spider has finished crawling, i.e., before a spider runs the log and data file
names are generated, the spider is called via blocking run with the twisted
reactor, the JSON data is compared for inventory changes (each spider is an
inventory watcher), and post all relevant messages to Slack. 
"""

import json
import logging
import time
import traceback
import sys
import os
import threading
import signal

from datetime import timedelta, datetime
from enum import Enum
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner

from utils import get_random_user_agent
from utils.compare_tools import compare_inventory_files, dprint
from utils.slack_tools import post_message, post_message_to_queue, DEBUG_SLACK_CHANNEL
from utils import message_formatter

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
    TERMINATED = 10


class Scraper(object):

    'Base class for all scrapers'

    def __init__(self, name, spider, slack_channel, product_link_formatter=message_formatter.DEFAULT_LINK_FORMATTER,\
        multiprocessing_queue=None, debug_flag=False, product_link=None):

        #todo argument check name, spider, slack_channel, product_link, etc

        self.__stage_lock = threading.Lock()
        self.stage = ScraperStage.CREATED #todo private access so public getter with lock?

        # name of the scraper
        self.name = name

        # spider object
        self.spider = spider

        # slack channel name used to post results
        self.slack_channel = slack_channel

        # link to use to append to an ID, todo need to make a rich object as links are page specific
        # either specify or leave blank
        self.product_link_formatter = product_link_formatter

        self.product_link = product_link

        #multiprocessing queue to post results, used among the various processes
        #to share a slack connection via slack tools
        self.multiprocessing_queue = multiprocessing_queue

        # base directory of scraper results
        self.base_directory = os.path.join(
            os.path.dirname(__file__), 'data/' + name)

        self.start_time = 0

        self.debug_log = debug_flag
        self.debug_slack = debug_flag

    def initialize(self):
        """
        Setup everything necessary for each run. Mainly file system folders,
        desintations, JSON data file names, log names, logger setup etc.
        """

        self.set_stage(ScraperStage.INITIALIZED)
        self.start_time = 0
        now = datetime.now()
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

        self.check_and_setup_directories()

        # set logger name
        self.logger = logging.getLogger(__name__)

        # set format
        logging.basicConfig(filename=self.log_name, filemode='w', level=logging.INFO,
                            format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

        if self.debug_log:
            self.logger.setLevel(logging.DEBUG)


    def set_stage(self, new_stage):
        """
        Set the current stage of the scraper.
        """

        with self.__stage_lock:
            print(str(datetime.now()) + ' setting stage to ' + str(new_stage))
            self.stage = new_stage


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


    def terminate(self, signum, frame):
        """
        Method used as a callback for the SIGINT signal handler. 
        """
        self.set_stage(ScraperStage.TERMINATED)
        #stop the reactor
        reactor.stop()


    def check_and_setup_directories(self):

        # housekeeping for files storage, e.g.
        # named directory for results
        if not os.path.isdir(self.base_directory):
            logging.info('creating ' + self.base_directory)
            os.makedirs(self.base_directory)

        if not os.path.isdir(self.archive_directory):
            logging.info('creating ' + self.archive_directory)
            os.makedirs(self.archive_directory)

        if not os.path.isdir(self.log_directory):
            logging.info('creating ' + self.log_directory)
            os.makedirs(self.log_directory)

        # check if a results file exists (it shouldn't if properly rotated)
        # shouldn't be possible now with timestamp
        if os.path.isfile(self.new_file_name):
            logging.warn(self.new_file_name + ' + already exists!')


    def run_spider(self):
        """
        Rather than using scrapyd or executing the spider manually via scrapy,
        this method creates a CrawlerRunnerand runs the spider provided at
        construction.

        https://doc.scrapy.org/en/latest/topics/practices.html#run-from-script
        http://twistedmatrix.com/trac/wiki/FrequentlyAskedQuestions#Igetexceptions.ValueError:signalonlyworksinmainthreadwhenItrytorunmyTwistedprogramWhatswrong
        """
        try:

            self.set_stage(ScraperStage.CRAWLING)
            self.start_time = time.time()

            # post debug message to slack
            if self.debug_slack:
                self.handle_slack_message(DEBUG_SLACK_CHANNEL, 'Starting scraper ' + self.name)

            #configure_logging( {'LOG_FORMAT': '%(levelname)s: %(message)s'} )
            runner = CrawlerRunner({
                'USER_AGENT': get_random_user_agent.get_random_user_agent(),
                'FEED_FORMAT': 'json',
                'FEED_URI': self.new_file_name,
                'AUTOTHROTTLE_ENABLED': 'True',
                'DUPEFILTER_DEBUG': 'True'
            })

            # todo deferred spider or something like
            # https://kirankoduru.github.io/python/multiple-scrapy-spiders.html
            _d = runner.crawl(self.spider)

            # stop the reactor when we're done
            _d.addBoth(lambda _: reactor.stop()) 
            #http://twistedmatrix.com/documents/9.0.0/core/howto/deferredindepth.html#auto7
            #https://twistedmatrix.com/documents/17.9.0/api/twisted.internet.defer.Deferred.html
            signal.signal(signal.SIGINT, self.terminate)
            signal.signal(signal.SIGTERM, self.terminate)
            reactor.run()
            # this will block until stop is called / when the crawler is done

            return True, None

        except KeyboardInterrupt:
            raise KeyboardInterrupt("KeyboardInterrupt caught in run")
        except Exception as _e:
            exc_type, exc_value, exec_tb = sys.exc_info()
            return False, 'Caught ' \
                + str("".join(traceback.format_exception(exc_type, exc_value, exec_tb)))


    def process_spider_results(self):
        """
        Process / Compare new results obtained from the associated Spider in this class.
        If the inventory file does not exist, then the new file becomes our inventory.

        Otherwise, use the module compare_tools to obtain our added and removed
        items from inventory.
        """

        try:
            self.set_stage(ScraperStage.PROCESSING_RESULTS)

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
                'compare_inventory_files( ' + self.inventory_file_name + ", "
                + self.new_file_name + " )")
            removed, added = compare_inventory_files(
                self.inventory_file_name, self.new_file_name)

            # debug printing
            dprint(removed, added)

            # now we have a new inventory file, rotating to inventory_file_name
            now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            self.rotated_file_name = self.rotated_file_name + now + '.json'

            logging.debug('rotating ' + self.inventory_file_name +
                          ' to ' + self.rotated_file_name)

            os.rename(self.inventory_file_name, self.rotated_file_name)
            os.rename(self.new_file_name, self.inventory_file_name)

            # compile results
            results = {}
            results[message_formatter.ADDED_MAP_KEY] = added
            results[message_formatter.REMOVED_MAP_KEY] = removed

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
                

    def post_crawl(self):
        """
        Process results and post messages to slack after the spider has completed
        crawling.
        """

        self.set_stage(ScraperStage.POST_CRAWL)

        # Now attempt to obtain results
        success, results = self.process_spider_results()

        if not success:
            error_message = 'process_spider_results failed\n' + results
            self.logger.error(error_message)
            self.report_errors_to_slack(error_message)
            self.set_stage(ScraperStage.TERMINATED)
            return False, error_message

        # post the results to slack
        #todo deprecate post_to_slack
        message = self.handle_results(results)

        # post to debug slack
        if self.debug_slack:
            self.handle_slack_message(DEBUG_SLACK_CHANNEL, 'Finished crawler ' + self.name \
                    + ', time taken = ' + str(timedelta(seconds=(time.time() - self.start_time))) \
                    + ((',' + message) if len(message) > 0 else ''))

        return True, message

    def handle_results(self, compared_results):
        #get the message
        
        #legacy link
        link_lambda = self.product_link_formatter
        if self.product_link is not None:
            link_lambda = lambda _id,_name: _name + " : " + self.product_link + _id

        should_post, message = message_formatter.format_notification_message(compared_results, link_lambda)
        
        #post to slack if anything was added
        if should_post:
            self.set_stage(ScraperStage.POSTING_RESULTS)
            self.handle_slack_message(self.slack_channel, message)

        #return the message
        return message

    def report_errors_to_slack(self, error_message):
        """
        Report / post the input error message to the debug slack channel.
        """
        self.handle_slack_message(DEBUG_SLACK_CHANNEL, error_message)


    def handle_slack_message(self, slack_channel, message):
        """
        Post a message to slack. Use the slack_tools module unless
        the multiprocessing queue has been set via the constructor. 
        """

        self.logger.info('handle_slack_message ' + str(slack_channel) + " " + str(message))

        if self.multiprocessing_queue is not None:

            self.logger.info('handle_slack_message posting to queue')
            post_message_to_queue(self.multiprocessing_queue, slack_channel, message)

        else:

            self.logger.info('handle_slack_message post_message')
            post_message(slack_channel, message)


    def run(self):
        """ Blocking run.

        Main workhorse method of the class. It creates and runs the spider,
        new file output to stored inventory,
        processes and saves results, and then posts to the appropriate Slack
        channel.

        TODO could subclass from thread or process
        """

        self.initialize()
        self.set_stage(ScraperStage.RUNNING) #todo not needed..?

        success, message = self.run_spider()

        if not success or self.stage == ScraperStage.TERMINATED:

            error_message = 'run_spider failed:' + ( " " + str(message) if message else "") \
                + (" Manually terminated" if self.stage == ScraperStage.TERMINATED else "")
            self.logger.error(error_message)
            self.report_errors_to_slack(error_message)
            self.set_stage(ScraperStage.TERMINATED)
            return False, error_message
        
        success, message = self.post_crawl()

        self.set_stage(ScraperStage.FINISHED)
        return True, message

