from scraper   import *
from knlSpider import *
import logging

knl = Scraper( 'knl', KnLBeerSpider, 'http://www.klwines.com/p/i?i=', 'knlscraper' )

knl.scrape()