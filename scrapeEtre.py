from scraper   import *
from etreSpider import *

etre = Scraper( 'etre', EtreSpider, 'http://www.bieresgourmet.be/catalog/index.php?main_page=product_info&products_id=', 'etrescraper' )
etre.scrape()