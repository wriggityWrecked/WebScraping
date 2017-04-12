from scraper    import *
from spiders.etreSpider import EtreSpider
import threading

lock = threading.Lock()

def run():
	global lock
	with lock:
		etre = Scraper( 'etre', EtreSpider, 'http://www.bieresgourmet.be/catalog/index.php?main_page=product_info&products_id=', 'etrescraper' )
		etre.run()

def isRunning():
	#todo return status
	global lock
	if lock.locked():
		return True
	else:
		return False

def main():
	run()

if __name__ == "__main__":
	main()