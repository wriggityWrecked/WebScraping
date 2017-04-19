from scraper    import *
from spiders.biabSpider import *
import threading

lock = threading.Lock()

def run():
	global lock
	with lock:
		#link looks like https://belgiuminabox.com/shop/beer/6004-3-fonteinen-intense-red-oude-kriek-2016-75-cl.html
		biab = Scraper( 'biab', BelgiumInABox, "", 'biabscraper' )
		biab.run() #this no longer blocks!!!!

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