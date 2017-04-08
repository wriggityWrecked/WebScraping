from scraper   import *
from belgianHappinessSpider import *
import threading

lock = threading.Lock()

def run():
	global lock
	with lock:
		bh = Scraper( 'belgianHappiness', BelgianHappinessSpider, "", 'belgianHappiness' )
		bh.run()

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