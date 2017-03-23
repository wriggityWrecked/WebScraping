import json
import sys
import filecmp
import os
from pprint import pprint
import logging

def compareMap( oldMap, newMap ):

	#print str ( len( oldMap ) ) 
	#print str ( len( newMap ) ) 

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

def compareInventories( inventoryFile, newFile ):

	r = {}
	n = {}

	if not os.path.isfile( inventoryFile ):
		logging.error( str( inventoryFile ) + ' not found!' )
		#todo alert for error, return empties
		return r,n

	if os.stat( inventoryFile ).st_size == 0:
		logging.error(  str( inventoryFile ) + ' is empty!' )
		#todo alert for error, return empties
		return r,n

	if not os.path.isfile( newFile ):
		logging.error(  str( newFile ) + ' not found!' )
		#todo alert for error, return empties
		return r,n8

	if os.stat( newFile ).st_size == 0:
		logging.error(  str( newFile ) + ' is empty!' )
		#todo alert for error, return empties
		return r,n

	if filecmp.cmp(inventoryFile, newFile, shallow=False):
		logging.inform(  str( inventoryFile ) + ' is equal to ' + str( newFile ) + ', no differences!' )
		return r,n

	#print '=================================================================='	
	#print( 'Comparing ' + str( inventoryFile )  + ' ' + str( newFile ) )


	hashMap1 = inventoryFile2Dictionary( inventoryFile )
	hashMap2 = inventoryFile2Dictionary( newFile )

	r, n = compareMap( hashMap1, hashMap2 )

	return r, n

def dprint( removed, added ):

	#print ''
	#print '=================================================================='
	logging.error( '' )
	logging.error( 'Removed: ' + str( len ( removed ) ) )
	logging.error( '' )
	logging.error( pprint( removed ) )
	logging.error( '' )
	logging.error( '==================================================================' )
	logging.error( '' )
	logging.error( 'Added:   ' + str( len ( added ) ) )
	logging.error( '' )
	logging.error( pprint( added ) )
	logging.error( '' )
	#print '=================================================================='

def main():

	#compare 2 files
	if len( sys.argv ) < 3:
		print 'must input two file names'
		return

	r,n = compareInventories( sys.argv[1], sys.argv[2] )
	dprint( r, n )

if __name__ == '__main__':
	main()
