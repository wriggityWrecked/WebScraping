import scrapy
import os
import datetime
import json
import logging
import time
import traceback
import sys
import getRandomUserAgent
from datetime           import timedelta
from pprint             import pprint
from scrapy.crawler     import CrawlerProcess
from compareInventories import *
from slackTools         import *


debugSlackChannel = 'robot_comms'

class Scraper:

	'Base class for all scrapers'

	def __init__( self, name, spider, productLink, slackChannel ):

		#name of the scraper
		self.name                  = name
		
		#spider object
		self.spider                = spider
		
		#link to use to append to an ID, todo need to make a rich object as links are page specific
		#either specify or leave blank
		self.productLink           = productLink
		
		#slack channel name used to post results                
		self.slackChannel          = slackChannel   
		
		#base directory of scraper results
		baseDirectory              = './' + name
		
		#archive directory of scraper results
		self.archiveDirectory      = baseDirectory         + '/' + datetime.datetime.now().strftime( "%Y-%m")   
		
		#file name to dump Spider JSON output  
		self.newFileName           = baseDirectory         + '/' + 'new_' + name + 'Result.json'
		
		#file name to keep as inventory file: used for all new vs old comparisons
		self.inventoryFileName     = baseDirectory         + '/' + name + 'BeerInventory.json'
		
		#file name for comparison results
		self.resultsOutputFileName = self.archiveDirectory + '/' + 'results_' + name + 'Beer' #append time and .json later
		
		#file name for old inventory data
		self.rotatedFileName       = self.archiveDirectory + '/' + 'old_' + name + '_'        #append time and .json later
		
		#logging directory for this scraper
		logDirectory               = baseDirectory         + '/' + 'log' 
		
		#log name each time run is called
		logName                    = logDirectory          + '/' + name + '_' + datetime.datetime.now().strftime( "%Y-%m-%dT%H:%M:%S" ) + '.log'

		self.checkAndSetupDirectories( baseDirectory, logDirectory )

		#set logger name
		logger = logging.getLogger( __name__ )
		
		#set format
		logging.basicConfig( filename=logName, filemode='w', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S' )

		#initialize
		self.startTime = 0

	def checkAndSetupDirectories( self, baseDirectory, logDirectory ):

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


	def runSpider( self ):
		"""
		Rather than using scrapyd or executing the spider manually via scrapy,
		this method creates a CrawlerProcess and runs the spider provided at
		construction. 
		"""
		try:
			self.startTime = time.time()
			
			#post debug message to slack
			postMessage( debugSlackChannel, 'Starting crawler ' + self.name )

			process = CrawlerProcess({
			    'USER_AGENT'           : getRandomUserAgent.getUserAgent(),
				'FEED_FORMAT'          : 'json',
				'FEED_URI'             : self.newFileName,
				'AUTOTHROTTLE_ENABLED' : 'True'
			})

			process.crawl( self.spider )
			process.start() # the script will block here until the crawling is finished

			return True, None

		except Exception as e:
			exc_type, exc_value = sys.exc_info()[:2]
			return False, 'Caught ' + str( traceback.format_exception_only( exc_type, exc_value ) ) 


	def processSpiderResults( self ):
		"""	
		Process / Compare new results obtained from the associated Spider in this class. 
		If the inventory file does not exist, then the new file becomes our inventory. 

		Otherwise, use the module compareInventories to obtain our added and removed 
		items from inventory. 
		"""

		try:
			#Crawling must be successful or the new file and inventory files
			#must exist as this point
			if not os.path.isfile( self.newFileName ):
				
				reason = str( self.newFileName ) + ' not found!'
				logging.warning( ( reason ) )
				
				return False, reason

			if not os.path.isfile( self.inventoryFileName ):
				reason = str( self.inventoryFileName ) + ' not found!' + 'saving ' + self.newFileName + ' as ' + self.inventoryFileName 
				
				logging.info( reason )
				os.rename( self.newFileName, self.inventoryFileName )
				
				return False, reason

			#Both files exist, OK to compare
			removed, added = compareInventories( self.inventoryFileName, self.newFileName )

			#debug printing
			dprint( removed, added )

			#now we have a new inventory file, rotating to inventoryFileName
			now                  = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
			self.rotatedFileName = self.rotatedFileName + now + '.json' 

			logging.debug( 'rotating ' + self.inventoryFileName + ' to ' + self.rotatedFileName )

			os.rename( self.inventoryFileName, self.rotatedFileName )
			os.rename( self.newFileName, self.inventoryFileName)

			#compile results
			results                  = {}
			results['addedLength']   = len ( added ) 
			results['addedList']     = added
			results['removedLength'] = len ( removed ) 
			results['removedList']   = removed

			logging.debug( 'results = ' + str( results ) )

			#save results
			self.resultsOutputFileName = self.resultsOutputFileName + '_' + now + '.json'
			with open( self.resultsOutputFileName, 'w') as outFile:
				logging.debug( 'saving ' + self.resultsOutputFileName )
				json.dump( results, outFile )

			return True, results

		except Exception as e:
			exc_type, exc_value = sys.exc_info()[:2]
			return False, 'Caught ' + str( traceback.format_exception_only( exc_type, exc_value ) ) 


	def postToSlack( self, results, slackChannel ):
		"""	
		Construct a results string, from the input, and post to the input Slack channel. 
		"""

		try:
			#post to slack
			if not self.productLink:
				postResultsToSlackChannel( results, slackChannel ) 
			else:
				postResultsToSlackChannelWithLink( results, self.productLink, slackChannel ) 


			ar = 'Added: ' + str( results['addedLength'] ) + ', Removed: ' + str( results['removedLength'] )
			#post to debug slack
			postMessage( debugSlackChannel, 'Finished crawler ' + self.name + ', '+ ar + ', time taken = ' + str( timedelta( seconds=( time.time() - self.startTime ) ) ) )

			return True, None

		except Exception:
			exc_type, exc_value = sys.exc_info()[:2]
			return False, 'Caught ' + str( traceback.format_exception_only( exc_type, exc_value ) ) 

	def reportErrorsToSlack( self, errorMessage ):
		try:

			postMessage( debugSlackChannel, errorMessage )
			return True, None

		except Exception:
			exc_type, exc_value = sys.exc_info()[:2]
			return False, 'Caught ' + str( traceback.format_exception_only( exc_type, exc_value ) ) 

	def run( self ):
		"""
		Main workhorse method of the class. It creates and runs the spider, compares new file output to stored inventory,
		processes and saves results, and then posts to the appropriate Slack channel. 
		"""

		#Psh whatever google style guide, I'll describe what I want.
		#Before you can walk, you must first crawl.
		success, message = self.runSpider()

		if not success:
			errorMessage = 'runSpider failed! ' + message 
			logger.error( errorMessage )
			self.reportErrorsToSlack( errorMessage )
			return

		#Now attempt to obtain results
		success, results = self.processSpiderResults()

		if not success:
			errorMessage = 'processSpiderResults failed! ' + results 
			logger.error( errorMessage )
			self.reportErrorsToSlack( errorMessage )
			return

		#post the results to slack	
		success, message = self.postToSlack( results, self.slackChannel )

		if not success:
			logger.error( 'postToSlack failed! ' + message )
			return
