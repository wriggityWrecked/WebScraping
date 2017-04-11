from scraper   import *
from spiders.knlSpider import KnLBeerSpider
import threading

lock = threading.Lock()
knl  = None

def run():

	global lock
	global knl

	lockAcquired = lock.acquire(False)

	if lockAcquired and knl == None:
		try:
			knl = Scraper( 'knl', KnLBeerSpider, 'http://www.klwines.com/p/i?i=', 'knlscraper' )
			knl.run() #this doesn't block!!!
		finally:
			lock.release()
			status = str( knl )
			knl    = None
			return True, status
	else:
		message = "Couldn't acquire lock" if knl == None else str( knl )
		return False, message

def isRunning():
	
	global lock
	global knl

	if lock.locked() or knl != None:
		return True
	else:
		return False

def main():
	"Run the scraper as a standalone"
	global knl
	knl = Scraper( 'knl', KnLBeerSpider, 'http://www.klwines.com/p/i?i=', 'knlscraper' )
	print knl.oneShot()

if __name__ == "__main__":
	main()