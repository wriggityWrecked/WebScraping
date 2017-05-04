"""Script to run Belgium Happiness scraper.

This module is simply a wrapper to instantiate a specific
scraper (BH) and run it. The main function will exit
when the scraper has completed its one_shot function.

Example:
	$ python scrape_belgian_happiness.py

"""

from spiders.belgianHappinessSpider import BelgianHappinessSpider
from scraper import Scraper


def main():
	"""Run the scraper as a standalone script."""

	bh_scraper = Scraper( 'belgianHappiness', BelgianHappinessSpider, "", 'belgianHappiness' )
	print bh_scraper.one_shot()


if __name__ == "__main__":
	main()
