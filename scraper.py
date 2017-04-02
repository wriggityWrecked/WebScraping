import scrapy
import os
import datetime
import json
import logging
from pprint             import pprint
from scrapy.crawler     import CrawlerProcess
from compareInventories import *
from slackTools         import *
from getRandomUserAgent import * 

class Scraper:
	'Base class for all scrapers'

	def __init__( self, name, spider, productLink, slackChannel ):

		self.name                  = name
		self.spider                = spider
		self.productLink           = productLink                #can be blank
		self.slackChannel          = slackChannel   
		baseDirectory              = './' + name
		self.archiveDirectory      = baseDirectory         + '/' + datetime.datetime.now().strftime( "%Y-%m")     
		self.newFileName           = baseDirectory         + '/' + 'new_' + name + 'Result.json'
		self.inventoryFileName     = baseDirectory         + '/' + name + 'BeerInventory.json'
		self.resultsOutputFileName = self.archiveDirectory + '/' + 'results_' + name + 'Beer' #append time and .json later
		self.rotatedFileName       = self.archiveDirectory + '/' + 'old_' + name + '_'        #append time and .json later
		logDirectory               = baseDirectory         + '/' + 'log' 
		logName                    = logDirectory          + '/' + name + '_' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + '.log'

		#housekeeping for files storage, e.g.
		#named directory for results
		if not os.path.isdir( baseDirectory ):
			logging.info( 'creating ' + baseDirectory )
			os.makedirs( baseDirectory )

		if not os.path.isdir( self.archiveDirectory ):
			logging.info( 'creating ' + self.archiveDirectory )
			os.makedirs( self.archiveDirectory )


		if not os.path.isdir( logDirectory ):
			logging.info( 'creating ' + logDirectory )
			os.makedirs( logDirectory )

		logger = logging.getLogger(__name__ + ':' + self.name)
		#todo UTC time
		logging.basicConfig(filename=logName, filemode='w', level=logging.DEBUG, format='%(asctime)s-%(module)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

	def scrape( self ):
		#todo this needs to be split up functionally with better error handling
		logger = logging.getLogger(__name__ + ':' + self.name)

		process = CrawlerProcess({
		    'USER_AGENT'           : getUserAgent(),
			'FEED_FORMAT'          : 'json',
			'FEED_URI'             : self.newFileName,
			'AUTOTHROTTLE_ENABLED' : 'True'
		})

		process.crawl( self.spider )
		process.start() # the script will block here until the crawling is finished

		#ok, so we finished crawling. do we have a new file?

		if not os.path.isfile( self.newFileName ):
			logging.warning( ( str( self.newFileName ) + ' not found!' ) )
			return

		if not os.path.isfile( self.inventoryFileName ):
			logging.warning( str( self.inventoryFileName ) + ' not found!' )
			logging.info( 'saving ' + self.newFileName + ' as ' + self.inventoryFileName )
			os.rename( self.newFileName, self.inventoryFileName )
			return

		#ok, let's compare files then!
		removed, added = compareInventories( self.inventoryFileName, self.newFileName )

		#debug printing
		dprint( removed, added )

		#now we have a new inventory file, rotating to inventoryFileName
		now                  = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		self.rotatedFileName = self.rotatedFileName + now + '.json' 

		logging.debug( 'rotating ' + self.inventoryFileName + ' to ' + self.rotatedFileName )

		os.rename( self.inventoryFileName, self.rotatedFileName )
		os.rename( self.newFileName, self.inventoryFileName)

		#write stats to file
		results                  = {}
		results['removedLength'] = len ( removed ) 
		results['removedList']   = removed
		results['addedLength']   = len ( added ) 
		results['addedList']     = added

		logging.debug( 'results = ' + str( results ) )

		#save results
		self.resultsOutputFileName = self.resultsOutputFileName + '_' + now + '.json'
		with open( self.resultsOutputFileName, 'w') as outfile:
		    json.dump( results, outfile )

		#post to slack
		if not self.productLink:
			postResultsToSlackChannel( results, self.slackChannel ) 
		else:
			postResultsToSlackChannelWithLink( results, self.productLink, self.slackChannel ) 

