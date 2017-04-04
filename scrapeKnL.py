from scraper   import *
from knlSpider import *

#todo command line options to post to slack

knl = Scraper( 'knl', KnLBeerSpider, 'http://www.klwines.com/p/i?i=', 'knlscraper' )
knl.scrape()