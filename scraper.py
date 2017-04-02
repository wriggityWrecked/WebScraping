import scrapy
import os
import datetime
import json
from pprint             import pprint
from scrapy.crawler     import CrawlerProcess
from etreSpider         import *
from compareInventories import *
from slackTools         import *

class Scraper:
	'Base class for all scrapers'

	def __init__( self, name, spider, productLink, slackChannel ):

		self.name                  = name
		self.spider                = spider
		self.newFileName           = 'new_' + name + 'Result.json'
		self.inventoryFileName     = name + 'BeerInventory.json'
		self.resultsOutputFileName = 'results_' + name + 'Beer' #append time and .json later
		self.rotatedFileName       = 'old_' + name              #append time and .json later
		self.productLink           = productLink                #can be blank
		self.slackChannel          = slackChannel              
		#todo really need to add a logger

		#todo housekeeping for files storage, e.g.
		#currentDirectory/name/year-month/
		#try to get it and if it doesn't exist then create (for current year and month)

	def scrape( self ):

		process = CrawlerProcess({
		    'USER_AGENT' : 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)', #todo need to rotate this out
			'FEED_FORMAT': 'json',
			'FEED_URI'   : self.newFileName
		})

		process.crawl( self.spider )
		process.start() # the script will block here until the crawling is finished

		#ok, so we finished crawling. do we have a new file?

		if not os.path.isfile( self.newFileName ):
			print( str( self.newFileName ) + ' not found!' )
			#todo alert for error
			return

		if not os.path.isfile( self.inventoryFileName ):
			print str( self.inventoryFileName ) + ' not found!'
			print 'saving ' + self.newFileName + ' as ' + self.inventoryFileName
			os.rename( self.newFileName, self.inventoryFileName )
			#todo alert for error
			return

		#ok, let's compare files then!
		removed, added = compareInventories( self.inventoryFileName, self.newFileName )

		#debug printing, todo need a logger
		dprint( removed, added )

		#now we have a new inventory file, rotating to inventoryFileName
		now                  = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		self.rotatedFileName = self.rotatedFileName + now + '.json' 

		print 'rotating ' + self.inventoryFileName + ' to ' + self.rotatedFileName

		os.rename( self.inventoryFileName, self.rotatedFileName )
		os.rename( self.newFileName, self.inventoryFileName)

		#write stats to file
		results                  = {}
		results['removedLength'] = len ( removed ) 
		results['removedList']   = removed
		results['addedLength']   = len ( added ) 
		results['addedList']     = added

		print ''
		print 'results = '  
		pprint( results )

		with open( self.resultsOutputFileName + '_' + now + '.json', 'w') as outfile:
		    json.dump( results, outfile )

		#post to slack

