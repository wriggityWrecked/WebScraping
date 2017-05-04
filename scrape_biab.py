"""Script to run Belgium in a Box Scraper.

This module is simply a wrapper to instantiate a specific
scraper (BIAB) and run it. The main function will exit
when the scraper has completed its one_shot function.

Example:
	$ python scrape_biab.py

"""

from spiders.biabSpider import BelgiumInABox
from scraper import Scraper


def main():
	"""Run the scraper as a standalone script."""

	biab_scraper = Scraper('biab', BelgiumInABox, "", 'biabscraper')
	print biab_scraper.one_shot()


if __name__ == "__main__":
	main()
