import scrapy
import datetime
import json
import logging
import time
import traceback
import sys
import os
import threading

from enum               import Enum
from datetime           import timedelta
from pprint             import pprint
from scrapy.crawler     import CrawlerProcess
from twisted.internet   import reactor
from scrapy.crawler     import CrawlerRunner
from scrapy.utils.log   import configure_logging

from utils                    import getRandomUserAgent
from utils.compareInventories import *
from utils.slackTools         import *

debugSlackChannel = 'robot_comms'

class ScraperStage(Enum):

	INITIALIZED        = 1
	RUNNING            = 2
	CRAWLING           = 3
	FINISHED_CRAWLING  = 4
	POST_CRAWL         = 5
	PROCESSING_RESULTS = 6
	POSTING_RESULTS    = 7
	FINISHED           = 8
	TERMINATED_ERROR   = 9

class Scraper:

	'Base class for all scrapers'

	def __init__( self, name, spider, productLink, slackChannel ):
		
		self.stageLock = threading.Lock()
		self.stage     = ScraperStage.INITIALIZED
		nowString      = datetime.datetime.now().strftime( "%Y-%m-%dT%H:%M:%S" )

		#name of the scraper
		self.name = name
		
		#spider object
		self.spider = spider
		
		#link to use to append to an ID, todo need to make a rich object as links are page specific
		#either specify or leave blank
		self.productLink = productLink
		
		#slack channel name used to post results                
		self.slackChannel = slackChannel   
		
		#base directory of scraper results
		baseDirectory = os.path.join( os.path.dirname( __file__ ), 'data/' + name )
		
		#archive directory of scraper results
		self.archiveDirectory = baseDirectory + '/' + datetime.datetime.now().strftime( "%Y-%m")   
		
		#file name to dump Spider JSON output
		#timestamp in case of failures  
		self.newFileName = baseDirectory + '/' + 'new_' + name + 'Result_' + nowString + '.json'

		#file name to keep as inventory file: used for all new vs old comparisons
		self.inventoryFileName = baseDirectory + '/' + name + 'BeerInventory.json'
		
		#file name for comparison results
		self.resultsOutputFileName = self.archiveDirectory + '/' + 'results_' + name + 'Beer' #append time and .json later
		
		#file name for old inventory data
		self.rotatedFileName = self.archiveDirectory + '/' + 'old_' + name + '_'              #append time and .json later
		
		#logging directory for this scraper
		logDirectory = baseDirectory + '/' + 'log' 
		
		#log name each time run is called
		logName = logDirectory + '/' + name + '_' + nowString + '.log'

		self.checkAndSetupDirectories( baseDirectory, logDirectory )

		#set logger name
		logger = logging.getLogger( __name__ )
		
		#set format
		logging.basicConfig( filename=logName, filemode='w', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S' )
		logger.setLevel( logging.INFO )

		#initialize
		self.startTime = 0

	def setStage( self, newStage ):
		
		with self.stageLock:
			print 'setting stage to ' + str( newStage )
			self.stage = newStage

	def __str__( self ):

		string = "Stage=" + str( self.stage )

		if self.startTime != 0:

			if self.stage == ScraperStage.FINISHED:
				string += ", Finished "
			else:
				string += ", Started "

			string += str( timedelta( seconds=( time.time() - self.startTime ) ) ) + " ago."

		return string

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

		#check if a results file exists (it shouldn't if properly rotated)
		#shouldn't be possible now with timestamp
		if os.path.isfile( self.newFileName ):
			logging.warn( self.newFileName + ' + already exists!' )


	def runSpider( self, oneShot ):
		"""
		Rather than using scrapyd or executing the spider manually via scrapy,
		this method creates a CrawlerRunnerand runs the spider provided at
		construction. 

		https://doc.scrapy.org/en/latest/topics/practices.html#run-from-script
		http://twistedmatrix.com/trac/wiki/FrequentlyAskedQuestions#Igetexceptions.ValueError:signalonlyworksinmainthreadwhenItrytorunmyTwistedprogramWhatswrong
		"""
		try:
			self.setStage( ScraperStage.CRAWLING )
			self.startTime = time.time()

			#post debug message to slack
			postMessage( debugSlackChannel, 'Starting scraper ' + self.name )
			
			#configure_logging( {'LOG_FORMAT': '%(levelname)s: %(message)s'} )
			runner = CrawlerRunner({
				'USER_AGENT'           : getRandomUserAgent.getUserAgent(),
				'FEED_FORMAT'          : 'json',
				'FEED_URI'             : self.newFileName,
				'AUTOTHROTTLE_ENABLED' : 'True'
			})

			d = runner.crawl( self.spider )

			if oneShot:
				logger.info('ONESHOT')
				#stop the reactor when we're done
				d.addBoth( lambda _: reactor.stop() )
				reactor.run() #this will block until stop is called
			else:
				#add a callback when we're finished
				d.addBoth( lambda _: self.postCrawl() )
				#todo someone else needs to handle this!
				if not reactor.running:
					threading.Thread( target=reactor.run, kwargs={'installSignalHandlers':0} ).start()

			return True, None

		except Exception as e:
			exc_type, exc_value, exec_tb = sys.exc_info()
			return False, 'Caught ' + str( "".join( traceback.format_exception( exc_type, exc_value, exec_tb ) ) ) 

	def processSpiderResults( self ):
		"""	
		Process / Compare new results obtained from the associated Spider in this class. 
		If the inventory file does not exist, then the new file becomes our inventory. 

		Otherwise, use the module compareInventories to obtain our added and removed 
		items from inventory. 
		"""

		try:
			self.setStage( ScraperStage.PROCESSING_RESULTS )

			#Crawling must be successful or the new file and inventory files
			#must exist as this point
			if not os.path.isfile( self.newFileName ):
				
				reason = str( self.newFileName ) + ' not found!'
				logging.warning( ( reason ) )
				
				return False, reason

			if not os.path.isfile( self.inventoryFileName ):
				reason = str( self.inventoryFileName ) + ' not found!' + ', saving ' + self.newFileName + ' as ' + self.inventoryFileName 
				
				logging.info( reason )
				os.rename( self.newFileName, self.inventoryFileName )
				
				return False, reason

			#Both files exist, OK to compare
			logging.debug( 'compareInventories( ' + self.inventoryFileName + ", " + self.newFileName + " )")
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
			exc_type, exc_value, exec_tb = sys.exc_info()
			return False, 'Caught ' + str( "".join( traceback.format_exception( exc_type, exc_value, exec_tb ) ) ) 


	def postToSlack( self, results, slackChannel ):
		"""	
		Construct a results string, from the input, and post to the input Slack channel. 
		"""

		try:

			self.setStage( ScraperStage.POSTING_RESULTS )

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
			exc_type, exc_value, exec_tb = sys.exc_info()
			return False, 'Caught ' + str( "".join( traceback.format_exception( exc_type, exc_value, exec_tb ) ) ) 

	def reportErrorsToSlack( self, errorMessage ):

		try:

			postMessage( debugSlackChannel, errorMessage )
			return True, None

		except Exception:
			exc_type, exc_value, exec_tb = sys.exc_info()
			return False, 'Caught ' + str( "".join( traceback.format_exception( exc_type, exc_value, exec_tb ) ) ) 

	def postCrawl( self ) : 
		self.setStage( ScraperStage.POST_CRAWL )

		#Now attempt to obtain results
		success, results = self.processSpiderResults()

		if not success:
			errorMessage = 'processSpiderResults failed\n' + results 
			logger.error( errorMessage )
			self.reportErrorsToSlack( errorMessage )
			self.setStage( ScraperStage.TERMINATED_ERROR )
			return False, errorMessage

		#post the results to slack	
		success, message = self.postToSlack( results, self.slackChannel )

		if not success:
			logger.error( 'postToSlack failed\n' + message )
			#self.setStage( ScraperStage.TERMINATED_ERROR )
			#return False, errorMessage

		return True, results

	def run( self ):
		"""
		Main workhorse method of the class. It creates and runs the spider, compares new file output to stored inventory,
		processes and saves results, and then posts to the appropriate Slack channel. 
		"""
		self.setStage( ScraperStage.RUNNING )

		#Psh whatever google style guide, I'll describe what I want.
		#Before you can walk, you must first crawl.
		
		success, message = self.runSpider( False )
		#this will callback 

		if not success:
			errorMessage = 'runSpider failed\n' + message 
			logger.error( errorMessage )
			self.reportErrorsToSlack( errorMessage )
			self.setStage( ScraperStage.TERMINATED_ERROR )
			return False, errorMessage

		return True, message

	def oneShot( self ):

		self.setStage( ScraperStage.RUNNING )

		success, message = self.runSpider( True )

		if not success:
			errorMessage = 'runSpider failed\n' + message 
			logger.error( errorMessage )
			self.reportErrorsToSlack( errorMessage )
			self.setStage( ScraperStage.TERMINATED_ERROR )
			return False, errorMessage

		success, message = self.postCrawl()

		self.setStage( ScraperStage.FINISHED )
		return True, message
