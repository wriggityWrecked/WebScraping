"""Script to run KNL Scraper.

This module is simply a wrapper to instantiate a specific
scraper (KNL) and run it. The main function will exit
when the scraper has completed its one_shot function.

Example:
    $ python scrape_knl.py -h

"""

import argparse

from multiprocessing import Process
from spiders.knl_beer_spider import KnLBeerSpider
from spiders.knl_spirits_spider import KnLSpiritsSpider
from scraper import Scraper


def beer_run():
    """Run the scraper as a standalone script. This method blocks until finished"""

    # todo load names from config, url from config, etc
    knl_beer_scraper = Scraper('knl', KnLBeerSpider,
                               'http://www.klwines.com/p/i?i=', 'knlscraper')

    print knl_beer_scraper.one_shot()


def spirits_run():
    """Run the scraper as a standalone script. This method blocks until finished"""

    # todo load names from config, url from config, etc
    knl_spirits_scraper = Scraper('knlSpirits', KnLSpiritsSpider,
                                  'http://www.klwines.com/p/i?i=', 'knlspiritsscraper')

    print knl_spirits_scraper.one_shot()


def run_both():
    """Run both beer and spirits scraper. This method blocks until finished.
    Must be done in separate processes."""

    print('\nRunning both\nStarting beer\n')

    _p = Process(target=beer_run, args=())
    _p.start()
    _p.join()

    print('\nFinished beer\nStarting spirits\n')

    _p = Process(target=spirits_run, args=())
    _p.start()
    _p.join()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Scrape KnL beer, spirits, or both')
    parser.add_argument('scraper_type', metavar='Scraper Type',
                        help='The scraper type (calling a spider) to run: beer, spirits, or both',
                        choices=['beer', 'spirits', 'both'])
    scraper_type = parser.parse_args().scraper_type

    if scraper_type == 'beer':
        beer_run()
    elif scraper_type == 'spirits':
        spirits_run()
    elif scraper_type == 'both':
        run_both()
    else:
        print('Unrecongized option: ' + str(scraper_type))
