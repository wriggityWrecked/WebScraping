import json
import sys
import filecmp
import os
from pprint import pprint
import logging

logger = logging.getLogger(__name__)

def compareMap( oldMap, newMap ):
	
	removedEntries = {}
	newEntries     = {}

	for entry in newMap.keys():
		#check if in map1
		if entry not in oldMap:
			newEntries[entry] = newMap[entry]

	for entry in oldMap.keys():
		#check if in map1
		if entry not in newMap:
			removedEntries[entry] = oldMap[entry]

	return removedEntries, newEntries

def inventoryFile2Dictionary( inventoryFile ):

	d = {}
	with open( inventoryFile ) as f:    
	    data = json.load(f)
	    for line in data:
	    	if 'creationDate' not in line:
				d[ line['id'] ] = line[ 'name' ].encode( "utf8" )

	return d

def resultsFile2Dictionary( resultsFile ):
	
	d = {}

	if not os.path.isfile( resultsFile ):
		logging.error( str( resultsFile ) + ' not found!' )
		return d

	if os.stat( resultsFile ).st_size == 0:
		logging.error(  str( resultsFile ) + ' is empty!' )
		return d
		
	with open( resultsFile ) as f:    
	    d = json.load(f)
	return d

def compareInventories( inventoryFile, newFile ):

	r = {}
	n = {}

	if not os.path.isfile( inventoryFile ):
		logging.error( str( inventoryFile ) + ' not found!' )
		#todo alert for error, return empties
		return r,n

	if os.stat( inventoryFile ).st_size == 0:
		logging.error( str( inventoryFile ) + ' is empty!' )
		#todo alert for error, return empties
		return r,n

	if not os.path.isfile( newFile ):
		logging.error( str( newFile ) + ' not found!' )
		#todo alert for error, return empties
		return r,n

	if os.stat( newFile ).st_size == 0:
		logging.error( str( newFile ) + ' is empty!' )
		#todo alert for error, return empties
		return r,n

	if filecmp.cmp( inventoryFile, newFile, shallow=False ):
		logging.info( str( inventoryFile ) + ' is equal to ' + str( newFile ) + ', no differences!' )
		return r,n

	#todo need a way to compare and ignore the creation date
	#http://stackoverflow.com/questions/16275402/ignoring-lines-while-comparing-files-using-python

	hashMap1 = inventoryFile2Dictionary( inventoryFile )
	hashMap2 = inventoryFile2Dictionary( newFile )

	r, n = compareMap( hashMap1, hashMap2 )

	return r, n

def dprint( removed, added ):

	logging.info( '' )
	logging.info( '' )
	logging.info( 'Added:   ' + str( len ( added ) ) )
	logging.info( '' )
	logging.info( pprint( added ) )
	logging.info( '==================================================================' )
	logging.info( 'Removed: ' + str( len ( removed ) ) )
	logging.info( '' )
	logging.info( pprint( removed ) )
	logging.info( '' )
	logging.info( '' )

def main():

	#compare 2 files
	if len( sys.argv ) < 3:
		print 'must input two file names'
		return

	r,n = compareInventories( sys.argv[1], sys.argv[2] )
	dprint( r, n )

if __name__ == '__main__':
	main()
