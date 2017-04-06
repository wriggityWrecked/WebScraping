from scraper   import *
from knlSpider import *

#todo command line options to post to slack
def main():
	knl = Scraper( 'knl', KnLBeerSpider, 'http://www.klwines.com/p/i?i=', 'knlscraper' )
	knl.run()

if __name__ == "__main__":
	main()