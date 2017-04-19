from spiders.knlSpider import KnLBeerSpider
from scraper import Scraper


def main():
    """Run the scraper as a standalone script."""

    knlScraper = Scraper('knl', KnLBeerSpider,
                  'http://www.klwines.com/p/i?i=', 'knlscraper')
    print knlScraper.oneShot() #this blocks


if __name__ == "__main__":
    main()
