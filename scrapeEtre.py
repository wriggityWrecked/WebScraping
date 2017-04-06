from scraper   import *
from etreSpider import *

def main():

	etre = Scraper( 'etre', EtreSpider, 'http://www.bieresgourmet.be/catalog/index.php?main_page=product_info&products_id=', 'etrescraper' )
	etre.run()

if __name__ == "__main__":
	main()