from scraper   import *
from knlSpider import *
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
			knl.run()
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
	print run()

if __name__ == "__main__":
	main()