import logging
import os
from random import *

userAgentFile    = os.path.join( os.path.dirname( __file__ ), './userAgentList.txt' )
defaultUserAgent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
logger           = logging.getLogger( __name__ )

def getUserAgent():

	#does the file exist?
	if not os.path.isfile( userAgentFile ):
		logging.error( str( userAgentFile ) + ' not found!' )
		return defaultUserAgent

	#todo get the upper bound from the file (line number)
	randomLineNumber = randint( 1, 82 )
	count            = 0

	with open( userAgentFile ) as f:   
		for line in f:
			if count == randomLineNumber:
				toReturn = str( line.strip() )
				logging.info('chose ' + toReturn)
				return toReturn
			else:
				count += 1

	logging.error( 'Unable to choose a random line! ' + str( randomLineNumber ) )
	return defaultUserAgent