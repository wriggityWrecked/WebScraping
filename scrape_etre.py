"""Script to run Etre Scraper.

This module is simply a wrapper to instantiate a specific
scraper (Etre) and run it. The main function will exit
when the scraper has completed its one_shot function.

Example:
	$ python scrape_etre.py

"""

from spiders.etreSpider import EtreSpider
from scraper import Scraper


def main():
    """Run the scraper as a standalone script."""

    etre_scraper = Scraper('etre', EtreSpider,
					'http://www.bieresgourmet.be/catalog/index.php?main_page\
					=product_info&products_id=', 'etrescraper')
    print etre_scraper.one_shot()


if __name__ == "__main__":
    main()
