"""Script to run a variety of Scrapers.

Example:
    $ python scrape_knl.py -h

"""

import argparse
import time

from datetime import datetime, timedelta
from multiprocessing import Process, Pool
from random import randint, normalvariate

from spiders.knl_beer_spider import KnLBeerSpider
from spiders.knl_spirits_spider import KnLSpiritsSpider
from spiders.knl_coming_soon import KnLComingSoonSpider
from spiders.etreSpider import EtreSpider
from spiders.belgianHappinessSpider import BelgianHappinessSpider
from spiders.biabSpider import BelgiumInABox
from spiders.total_wine_spider import TotalWineSpider

from scraper import Scraper


def total_wine(debug_flag=False, multiprocessing_queue=None):
    """Run the scraper as a standalone script. This method blocks until finished"""

    #todo should be renamed
    total_wine_scraper = Scraper('total_wine', TotalWineSpider,
                               'totalwinescraper', product_link='http://www.totalwine.com/p/',
                                multiprocessing_queue=multiprocessing_queue, debug_flag=debug_flag)

    print total_wine_scraper.run()


def knl_beer(debug_flag=False, multiprocessing_queue=None):
    """Run the scraper as a standalone script. This method blocks until finished"""

    #todo should be renamed
    knl_beer_scraper = Scraper('knl', KnLBeerSpider,
                               'knlscraper', product_link='http://www.klwines.com/p/i?i=',
                                multiprocessing_queue=multiprocessing_queue, debug_flag=debug_flag)

    print knl_beer_scraper.run()


def knl_spirits(debug_flag=False, multiprocessing_queue=None):
    """Run the scraper as a standalone script. This method blocks until finished"""

    knl_spirits_scraper = Scraper('knlSpirits', KnLSpiritsSpider,
                                   'knlspiritsscraper', product_link='http://www.klwines.com/p/i?i=',
                                    multiprocessing_queue=multiprocessing_queue, debug_flag=debug_flag)

    print knl_spirits_scraper.run()


def knl_coming_soon(debug_flag=False, multiprocessing_queue=None):
    """Run the scraper as a standalone script. This method blocks until finished"""

    knl_coming_soon_scraper = Scraper('knlComingSoon', KnLComingSoonSpider,
                                   'knlcomingsoon', product_link_formatter=lambda _id,_name: _name + ' : http://www.klwines.com/p/i?i=' + _id,
                                    multiprocessing_queue=multiprocessing_queue, debug_flag=debug_flag)

    print knl_coming_soon_scraper.run()

def etre(debug_flag=False, multiprocessing_queue=None):
    """Run the scraper as a standalone script. This method blocks until finished"""
    
    etre_scraper = Scraper('etre', EtreSpider,
                    'etrescraper', product_link='http://www.bieresgourmet.be/catalog/index.php?main_page\
                    =product_info&products_id=', multiprocessing_queue=multiprocessing_queue, debug_flag=debug_flag)

    print etre_scraper.run()


def biab(debug_flag=False, multiprocessing_queue=None):
    """Run the scraper as a standalone script. This method blocks until finished"""

    biab_scraper = Scraper('biab', BelgiumInABox, 'biabscraper', multiprocessing_queue=multiprocessing_queue, debug_flag=debug_flag)

    print biab_scraper.run()


def belgium_happiness(debug_flag=False, multiprocessing_queue=None):
    """Run the scraper as a standalone script. This method blocks until finished"""

    bh_scraper = Scraper('belgianHappiness', BelgianHappinessSpider, 'belgianhappiness', 
        multiprocessing_queue=multiprocessing_queue, debug_flag=debug_flag)

    print bh_scraper.run()

#rename run serial
def run(methods_to_run, debug_flag=False, multiprocessing_queue=None):
    """Run input method(s) as a process. This method blocks until finished.

    Must be done in separate processes due to twisted reactor behavior.
    """

    #this is stupid, you're running processes so dont' serialize!
    #https://docs.python.org/2/library/multiprocessing.html#module-multiprocessing.pool
    for method in methods_to_run:
        print('\n' + str(datetime.now()) + ' Starting ' + str(method))
        _p = Process(target=method, args=(), kwargs={'debug_flag': debug_flag,
         'multiprocessing_queue':multiprocessing_queue})
        _p.start()
        _p.join()

        #todo time each run

    print('\n' + str(datetime.now()) + ' Finished ' + str(method) + ' \n')

#fun exercise, needs to be used in the scheduler
def run_parallel(methods_to_run, debug_flag=False, multiprocessing_queue=None):
    """Run input method(s) as a process. This method blocks until finished.

    Must be done in separate processes due to twisted reactor behavior.
    """

    #this is stupid, you're running processes so don't serialize!
    #https://docs.python.org/2/library/multiprocessing.html#module-multiprocessing.pool

    #todo submit an extra function for the queue to process results 

    pool = Pool(len(methods_to_run)) #-> this should use a QUEUE since everything is async!

    for method in methods_to_run:
        print('\n' + str(datetime.now()) + 'Starting ' + str(method))
        
        pool.apply_async(method, args=(), kwds={'debug_flag': debug_flag,
         'multiprocessing_queue':multiprocessing_queue})

    pool.close()
    pool.join()

    print('\n' + str(datetime.now()) + 'Finished\n')


def run_continuous(methods_to_run, debug_flag=False, lower_bound_seconds=1*60, upper_bound_seconds=2*60):
    """
    Hackish method to run manually via command line with a random sleep interval. 
    """

    #todo use lamba to generate random number https://docs.python.org/2/tutorial/controlflow.html#lambda-expressions
    #or just function call based on user input, but passing in a lambda would be nice
    try:

        while True:

            #todo time this
            run(methods_to_run, debug_flag)

            random_wait_time_seconds = randint(lower_bound_seconds, upper_bound_seconds)
            #     random_wait_time_seconds = normalvariate(25*60, 5*60)

            minutes, seconds = divmod(random_wait_time_seconds, 60)
            hours, minutes = divmod(minutes, 60)

            now = datetime.now()
            then = now + timedelta(hours=hours, minutes=minutes, seconds=seconds)

            print('\n' + str(now) + ' sleeping ' + str(minutes) + 'm' +
                str(seconds) + 's, will run at ' + str(then))

            time.sleep(random_wait_time_seconds) #todo threading.Timer?

            #https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python

    except KeyboardInterrupt:
        print '\nKeyboardInterrupt caught, exiting\n'


if __name__ == "__main__":

    #scraper_names input arguments to function
    #todo dynamic
    #https://stackoverflow.com/questions/5910703/howto-get-all-methods-of-a-python-class-with-given-decorator
    methods = {knl_beer.__name__: knl_beer, knl_spirits.__name__: knl_spirits,
        etre.__name__: etre, biab.__name__: biab, belgium_happiness.__name__: belgium_happiness,
        total_wine.__name__: total_wine, knl_coming_soon.__name__: knl_coming_soon}

    parser = argparse.ArgumentParser(
        description='Invoke implemented scrapers by name with run options.')

    parser.add_argument('scraper_names', metavar='Scraper Name(s)', nargs='+',
                        choices=methods.keys(),
                        help='The scraper name (calling a spider) to run. Choices: %(choices)s')

    parser.add_argument('-c', "--continuous", action='store_true',
                        help='Run the specified scraper(s) continuously. Default is to only run once')

    parser.add_argument('-d', "--debug", action='store_true',
                        help='Run the specified scraper(s) in debug mode')

    scraper_names = parser.parse_args().scraper_names
    continuous = parser.parse_args().continuous
    debug_flag = parser.parse_args().debug

    #get methods from string inputs
    method_list = []    
    for name in scraper_names:
        method_list.append(methods[name])

    if continuous is True:
        print 'Running ' + str(method_list) + " continuously"
        run_continuous(method_list, debug_flag=debug_flag)
    else:
        print 'Running ' + str(method_list) + " once"
        run(method_list, debug_flag=debug_flag)
