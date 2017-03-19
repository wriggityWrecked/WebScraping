import scrapy
import os
import datetime
import json
from pprint             import pprint
from scrapy.crawler     import CrawlerProcess
from etreSpider         import *
from compareInventories import *

newFileName           = 'newEtreResult.json'
inventoryFileName     = 'etreBeerInventory.json'
resultsOutputFileName = 'results_etreBeer'

def main():

	#todo random user agent

	# #todo get the file name
	# process = CrawlerProcess({
	#     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
	# 	'FEED_FORMAT': 'json',
	# 	'FEED_URI': newFileName
	# })

	# process.crawl( EtreSpider )
	# process.start() # the script will block here until the crawling is finished

	#ok, so we finished crawling. do we have a new file?
	#first, check if we have an inventory


	if not os.path.isfile( newFileName ):
		print str( newFileName ) + ' not found!'
		#todo alert for error
		return

	if not os.path.isfile( inventoryFileName ):
		print str( inventoryFileName ) + ' not found!'
		print 'saving ' + newFileName + ' as ' + inventoryFileName
		os.rename( newFileName, inventoryFileName )
		#todo alert for error
		return

	#ok, let's compare files then!
	removed, added = compareInventories( inventoryFileName, newFileName )
	
	#debug printing, todo need a logger
	print '================================='
	print 'Removed ' + str( len ( removed ) )
	pprint( removed )
	print '================================='
	print 'Added ' + str( len ( added ) )
	pprint( added )

	#now we have a new inventory file, rotating to inventoryFileName
	now             = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
	rotatedFileName = 'oldEtreBeer_' + now + '.json' 

	print 'rotating ' + inventoryFileName + ' to ' + rotatedFileName

	os.rename( inventoryFileName, rotatedFileName )
	os.rename( newFileName, inventoryFileName)

	#write stats to file
	results                  = {}
	results['removedLength'] = len ( removed ) 
	results['removedList']   = removed
	results['addedLength']   = len ( added ) 
	results['addedList']     = added

	pprint( results )

	with open( resultsOutputFileName + '_' + now + '.json', 'w') as outfile:
	    json.dump( results, outfile )


if __name__ == '__main__':
	main()