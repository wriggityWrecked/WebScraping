import json
import sys
import filecmp
import os
import logging

from subprocess  import *
from pprint      import pprint


logger          = logging.getLogger(__name__)
creationDateKey = 'creationDate'

def compareMap( oldMap, newMap ):
	
	removedEntries = {}
	newEntries     = {}

	for entry in newMap.keys():
		#check if in oldMap
		if entry not in oldMap:
			newEntries[entry] = newMap[entry]

	for entry in oldMap.keys():
		#check if in newMap
		if entry not in newMap:
			removedEntries[entry] = oldMap[entry]

	return removedEntries, newEntries

def inventoryFile2Dictionary( inventoryFile ):

	d = {}

	if not os.path.isfile( inventoryFile ):
		logging.error( str( inventoryFile ) + ' not found!' )
		return d

	if os.stat( inventoryFile ).st_size == 0:
		logging.error(  str( inventoryFile ) + ' is empty!' )
		return d

	with open( inventoryFile ) as f:    
	    data = json.load(f)
	    for line in data:
	    	if creationDateKey not in line:
				d[ line['id'] ] = line[ 'name' ].encode( "utf8" )

	return d

def compareInventories( inventoryFile, newFile ):

	r = {}
	n = {}

	if not os.path.isfile( inventoryFile ):
		logging.error( str( inventoryFile ) + ' not found!' )
		return r,n

	if os.stat( inventoryFile ).st_size == 0:
		logging.error( str( inventoryFile ) + ' is empty!' )
		return r,n

	if not os.path.isfile( newFile ):
		logging.error( str( newFile ) + ' not found!' )
		return r,n

	if os.stat( newFile ).st_size == 0:
		logging.error( str( newFile ) + ' is empty!' )
		return r,n

	if filecmp.cmp( inventoryFile, newFile, shallow=False ):
		logging.info( str( inventoryFile ) + ' is equal to ' + str( newFile ) + ', no differences!' )
		return r,n

	#todo need a way to either get rid of creation date (to compare files) or ignore first few lines

	#use bash to compare so we ourselves don't have to go through line by line
	#"diff  <(tail -n +3 " + file1 + ") <(tail -n +3 " + file2 + ") --strip-trailing-cr | wc -l"
	#subprocess.call('diff  <(tail -n +3 ' + 'old_knl_2017-04-10T16:08:57.json' + ') <(tail -n +3 ' + 'old_knl_2017-04-10T23:09:04.json' + ') --strip-trailing-cr', shell=True)
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