from scraper   import *
from belgianHappinessSpider import *

bh = Scraper( 'belgianHappiness', BelgianHappinessSpider, "", 'belgianHappiness' )
bh.scrape()