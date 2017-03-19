import json
import sys
import filecmp
import os.path
from pprint import pprint

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

def compareInventories( inventoryFile, newFile ):

	r = {}
	n = {}

	if not os.path.isfile( inventoryFile ):
		print str( inventoryFile ) + ' not found!'
		#todo alert for error, return empties
		return r,n

	if not os.path.isfile( newFile ):
		print str( newFile ) + ' not found!'
		#todo alert for error, return empties
		return r,n

	if filecmp.cmp(inventoryFile, newFile, shallow=False):
		print str( inventoryFile ) + ' is equal to ' + str( newFile ) + ', no differences!'
		return r,n

	print( 'Comparing ' + str( inventoryFile )  + ' ' + str( newFile ) )

	hashMap1 = {}
	with open( inventoryFile ) as f:    
	    data = json.load(f)
	    for line in data:
	    	#construct dictionary, specific to KnL output
	    	hashMap1[ line['id']] = line['name'].encode("utf8")

	#pprint(hashMap1)

	hashMap2 = {}
	with open( newFile ) as f:    
	    data = json.load(f)
	    for line in data:
	    	#construct dictionary
	    	hashMap2[ line['id']] = line['name'].encode("utf8")

	#pprint(hashMap2)

	r, n = compareMap( hashMap1, hashMap2 )

	#print '================================='
	#print 'Removed ' + str( len ( r ) )
	#pprint( r )
	#print '================================='
	#print 'Added ' + str( len ( n ) )
	#pprint( n )

	return r, n
