"""Script to run KNL Scraper.

This module is simply a wrapper to instantiate a specific
scraper (KNL) and run it. The main function will exit
when the scraper has completed its one_shot function.

Example:
    $ python scrape_knl.py -h

"""

import argparse
import time

from datetime import datetime, timedelta
from multiprocessing import Process
from random import randint

from spiders.knl_beer_spider import KnLBeerSpider
from spiders.knl_spirits_spider import KnLSpiritsSpider
from spiders.etreSpider import EtreSpider

#todo import all other implemented spiders

from scraper import Scraper

def knl_beer():
    """Run the scraper as a standalone script. This method blocks until finished"""

    # todo load names from config, url from config, etc
    knl_beer_scraper = Scraper('knl', KnLBeerSpider,
                               'http://www.klwines.com/p/i?i=', 'knlscraper')

    print knl_beer_scraper.run()


def knl_spirits():
    """Run the scraper as a standalone script. This method blocks until finished"""

    # todo load names from config, url from config, etc
    knl_spirits_scraper = Scraper('knlSpirits', KnLSpiritsSpider,
                                  'http://www.klwines.com/p/i?i=', 'knlspiritsscraper')

    print knl_spirits_scraper.run()


def etre():
    """Run the scraper as a standalone script. This method blocks until finished"""
    
    etre_scraper = Scraper('etre', EtreSpider,
                    'http://www.bieresgourmet.be/catalog/index.php?main_page\
                    =product_info&products_id=', 'etrescraper')
    print etre_scraper.run()


def biab():
    """Run the scraper as a standalone script. This method blocks until finished"""

    biab_scraper = Scraper('biab', BelgiumInABox, "", 'biabscraper')
    print biab_scraper.run()


def belgium_happiness():
    """Run the scraper as a standalone script. This method blocks until finished"""

    bh_scraper = Scraper( 'belgianHappiness', BelgianHappinessSpider, "", 'belgianHappiness' )
    print bh_scraper.run()

def run(methods_to_run):
    """Run input method(s) as a process. This method blocks until finished.
    Must be done in separate processes due to twisted reactor behavior.

    A smarter way to do this would be to schedule all spiders to scrape at 
    once. 
    """

    for method in methods_to_run:
        print('\nStarting ' + str(method))
        _p = Process(target=method, args=())
        _p.start()
        _p.join()
        print('\nFinished ' + str(method) + '\n')


def run_continuous(methods_to_run):
    """
    Hackish method to run manually via command line with a random sleep interval. 
    """

    try:
        while True:

            run(methods_to_run)

            random_wait_minutes = randint(5*60, 20*60) #todo configurable range?
            minutes = int(random_wait_minutes / 60.)
            seconds = int((random_wait_minutes / 60. - minutes) * 60)
            now = datetime.now()
            then = now + timedelta(minutes=minutes,seconds=seconds)

            print('\n' + str(now) + ' sleeping ' + str(minutes) + 'm' +
                str(seconds) + 's, will run at ' + str(then))

            time.sleep(random_wait_minutes) #todo threading.Timer?

    except KeyboardInterrupt:
        print '\nKeyboardInterrupt caught, exiting\n'

if __name__ == "__main__":

    methods = {knl_beer.__name__: knl_beer, knl_spirits.__name__: knl_spirits,
        etre.__name__: etre, biab.__name__: biab, belgium_happiness.__name__: belgium_happiness}

    parser = argparse.ArgumentParser(
        description='Invoke implemented scrapers by name.')

    parser.add_argument('scraper_names', metavar='Scraper Name(s)', nargs='+',
                        help='The scraper name (calling a spider) to run.',
                        choices=methods.keys())

    parser.add_argument('-c', "--continuous", action='store_true',
                        help='Run the specified scraper(s) continuously')
    
    #todo debug level flag input when running

    scraper_names = parser.parse_args().scraper_names
    continuous = parser.parse_args().continuous

    #get methods from string inputs
    method_list = []
    for name in scraper_names:
        method_list.append(methods[name])

    if continuous is True:
        print 'Running ' + str(method_list) + " continuously"
        run_continuous(method_list)
    else:
        print 'Running ' + str(method_list) + " once"
        run(method_list)
