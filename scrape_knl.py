"""Script to run KNL Scraper.

This module is simply a wrapper to instantiate a specific
scraper (KNL) and run it. The main function will exit
when the scraper has completed its one_shot function.

Example:
	$ python scrape_knl.py

"""

from spiders.knl_beer_spider import KnLBeerSpider
from spiders.knl_spirits_spider import KnLSpiritsSpider

from scraper import Scraper


def beer_run():
    """Run the scraper as a standalone script."""

    #todo load names from config, url from config, etc
    knl_beer_scraper = Scraper('knl', KnLBeerSpider,
					'http://www.klwines.com/p/i?i=', 'knlscraper')

    print knl_beer_scraper.one_shot()	

def spirits_run():
    """Run the scraper as a standalone script."""

    #todo load names from config, url from config, etc
    knl_spirits_scraper = Scraper('knlSpirits', KnLSpiritsSpider,
					'http://www.klwines.com/p/i?i=', 'knlspiritsscraper')
    
    print knl_spirits_scraper.one_shot()	

def main():
	#beer_run()
	spirits_run()

if __name__ == "__main__":
    main()
