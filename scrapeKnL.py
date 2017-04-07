from scraper   import *
from knlSpider import *

def main():
	knl = Scraper( 'knl', KnLBeerSpider, 'http://www.klwines.com/p/i?i=', 'knlscraper' )
	knl.run()

if __name__ == "__main__":
	main()