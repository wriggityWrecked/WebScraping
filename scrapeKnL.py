from scraper   import *
from knlSpider import *

knl = Scraper( 'knl', KnLBeerSpider, 'http://www.klwines.com/p/i?i=', 'knlscraper' )
knl.scrape()