from slackclient        import SlackClient
from compareInventories import *
from pprint             import pprint
import os
import subprocess

logger = logging.getLogger(__name__)

#so far link format only really works for prepend
def constructSlackMessageWithLink( resultsDictionary, linkFormat ):

	#minimum looks like
	#{"addedLength": 0, "addedList": {}, "removedLength": 0, "removedList": {}}

	added       = 0
	addedList   = {}
	removed     = 0
	removedList = {}
	message     = ""
	ls          = linkFormat

	if 'addedLength' in resultsDictionary and 'addedList' in resultsDictionary:
		added     = int( resultsDictionary['addedLength'] )
		addedList = resultsDictionary['addedList']

	if added > 0 and len( addedList ) > 0:
		message = 'Added : ' + str( added )  + '\n\n\n'

		if len( ls ) > 0:
			#for now it's fine to append
			for t in addedList.items():
				message += t[1] + " : " + ls + str( t[0] ) + '\n\n'
		else:
			message += '\n\n'.join( ' : '.join( t ) for t in addedList.items() )

	if 'removedLength' in resultsDictionary and 'removedList' in resultsDictionary:
		removed     = int( resultsDictionary['removedLength'] )
		removedList = resultsDictionary['removedList']

	if removed > 0 and len( removedList ) > 0:
		if len( message ) > 0:
			message += '\n====================\n\n'

		message += 'Removed : ' + str( removed )  + '\n\n\n'

		if len( ls ) > 0:
			#for now it's fine to append
			for t in removedList.items():
				message += t[1] + " : " + ls + str( t[0] ) + '\n\n'
		else:
			message += '\n\n'.join( ' : '.join( t ) for t in removedList.items() )

	return message

def constructSlackMessage( resultsDictionary ):
	return constructSlackMessageWithLink( resultsDictionary, "" )

def postMessage( channel, message ):

	slackToken = "";
	with open( './slackToken' ) as f:  
		slackToken = str( f.read() ).strip()

	sc = SlackClient(slackToken.strip())

	#check if token is empty
	if not sc:
		logger.warn( 'Empty SlackToken!' )
		return

	#check channel
	if not channel:
		logger.warn( 'Empty channel!' )
		return

	#check if message is empty
	if not message:
		logger.warn( 'Empty message!' )
		return

	output =  sc.api_call(
	  'chat.postMessage',
	  channel = '#' + channel,
	  text    = message
	)
	logger.inform( output )

def postResultsToSlackChannelWithLink( resultsDictionary, linkFormat, channelName ):

	message = constructSlackMessageWithLink( resultsDictionary, linkFormat  )
	postMessage( channelName, message )

def postResultsToSlackChannel( resultsDictionary, channelName ):

	message = constructSlackMessage( resultsDictionary )
	postMessage( channelName, message )

def test( fileName, linkFormat, channelName ):

	rd      = resultsFile2Dictionary( fileName )
	message = constructSlackMessage( rd )

	if len( message ) > 0:
		print 'sending ' + message

	print '\n================\n\n'

	rd      = resultsFile2Dictionary( fileName )
	message = constructSlackMessageWithLink( rd, linkFormat )

	if len( message ) > 0:
		print 'sending ' + message
 		postMessage( channelName, message )
