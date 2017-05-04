"""Script to run KNL Scraper.

This module is simply a wrapper to instantiate a specific
scraper (KNL) and run it. The main function will exit
when the scraper has completed its one_shot function.

Example:
	$ python scrape_knl.py

"""

from spiders.knl_spider import KnLBeerSpider
from scraper import Scraper


def main():
    """Run the scraper as a standalone script."""

    knl_scraper = Scraper('knl', KnLBeerSpider,
					'http://www.klwines.com/p/i?i=', 'knlscraper')
    print knl_scraper.one_shot()


if __name__ == "__main__":
    main()
