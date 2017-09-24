from slackclient import SlackClient
from datetime    import timedelta
from subprocess  import *
from websocket   import *

import os
import datetime
import logging
import logging.handlers
import time
import traceback
import sys
import threading

from utils import robotTextResponses

#todo import from tools
tokenFilePathAndName = os.path.join( os.path.dirname( __file__ ), 'utils/slackToken' )
logDirectory         = './data/slackReceiverLog'
logFileName          = logDirectory + '/slackReceiverLog_' + datetime.datetime.now().strftime( "%Y-%m-%dT%H:%M:%S" ) + '.log'
commandKey           = 'bash'
commandChannel       = 'C4UC35TLN'
dbId                 = 'U4SDBCXBJ'
debugSlackChannel    = 'robot_comms'
scrapeKey            = 'scrape'
#scrapeOptionsMap     = { 'knl' : scrapeKnl, 'etre' : scrapeEtre, 'bh' : scrapeBelgianHappiness, 'biab' : scrapeBiab }
helpKey1             = 'help'
helpKey2             = '?'
maxKeepAlive         = 60

if not os.path.isdir( logDirectory ):
	print( 'creating ' + logDirectory )
	os.makedirs( logDirectory )

logger  = logging.getLogger( __name__ )
logging.basicConfig( filename=logFileName, filemode='w', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S' )
handler = logging.handlers.RotatingFileHandler( logFileName, maxBytes=5000, backupCount=5 )
logger.addHandler( handler )
logger.addHandler( logging.StreamHandler(sys.stdout) )
logger.setLevel( logging.INFO )

#todo global thread dictionary to keep track of manual scrapes
#this should be a lib (for fun text responses)
def handleText( text, channel, user ):

	logger.info( 'handleText: ' + text + ' ' + channel + ' ' + user )

	if not text:
		logger.warn( 'ignoring empty message' )
		return ''

	#todo CPU
	#todo diskspace

	#split on spaces and grab the first word
	key = text.split(" ")
	if  len( key ) == 0:
		logger.warn(  'empty key!' )
		return ''

	key = key[0]
	#handle scraping
	if key.lower() == scrapeKey.lower():
		return handleScrape( text.replace( scrapeKey + " ", "" ) )

	#handle commands
	if key.lower() == commandKey.lower():
		#there can only be one
		if user != dbId:
			return 'Sorry, you do not have permission do execute that command.'
		return handleCommand( text.replace( commandKey + " ", "" ) )

	if key.lower() == helpKey1 or key.lower() == helpKey2:
		return handleHelp()

	#no commands, let's have fun with parsing text
	parsed, response = robotTextResponses.handleTextInput( text )

	if parsed:
		return response 

	return ''

def handleCommand( command ):

	logger.info( 'handleCommand: ' + str( command ) )

	try:

		p              = Popen( command, shell=True, stdout=PIPE )
		stdout, stderr = p.communicate()
		
		logger.debug( stdout )
		logger.debug( stderr )

		return str( stdout ) + '\n' + str( stderr )

	except Exception as e:
		exc_type, exc_value, exc_tb = sys.exc_info()
		return False, 'Caught ' + str( "".join( traceback.format_exception( exc_type, exc_value, exc_tb ) ) )

def handleScrape( command ):

	command = command.strip().lower()
	logger.info( 'handleScrape: ' + command )

	if command in scrapeOptionsMap:
		
		#todo scrape ALLLLLLLL

		target = scrapeOptionsMap[ command ]

		#check if already running
		if not getattr( target, 'isRunning')():
			#not foolproof, someone might have beat us to the punch
			#todo hang onto the thread to kill if taking too long, etc
			t = threading.Thread( target=getattr( target, 'run' ), args=() )
			#t.daemon = True
			t.start()

			return 'Acknowledged command, started manual ' + command + ' scraping'
		else:
			return 'Already running ' + str( target ) + '.\nPlease wait for completion.'

	#invalid scrape option
	return "Invalid scrape option: " + command + '\nAvailable options: ' + ', '.join( scrapeOptionsMap.keys() )

def handleHelp():
	helpMessage  = "Don't Panic\n\n" + "Available commands:\n\n" + "scrape [" 
	helpMessage += ' | '.join( scrapeOptionsMap.keys() )+ ']\n\n' + 'bash myBashCommand (only if you are theLostWizard)\n\n'
	return helpMessage

def sendReply( sc, ts, channelId, replyText ):
	"""http://slackapi.github.io/python-slackclient/real_time_messaging.html#connecting-to-the-real-time-messaging-api"""

	logger.debug( ts + ' ' + channelId + ' ' + replyText )
	#sc.rtm_send_message(replyText, channelId, ts, True) -- fails
	output = sc.api_call(
	  'chat.postMessage',
	  ts         = ts,
	  channel    = channelId,
	  text       = replyText,
      reply_broadcast=True
	)
	logger.debug( output )

def main():

	sleepTimeSeconds          = 60
	allowableTimeDeltaSeconds = 3 * sleepTimeSeconds
	slackToken                = "";

	with open( tokenFilePathAndName ) as f:  
		slackToken = str( f.read() ).strip()

	print slackToken
	sc = SlackClient( slackToken )
	#todo post hello

	if sc.rtm_connect():

		print sc.server
		keepAliveCount = 0

		while True:

			try:
				r = sc.rtm_read()
				logger.debug( str( time.time() ) + ' ' + str( r ) )

				#check time, if it's the time delta is greater than our polling then       
				if len( r ) > 0:
					keepAliveCount = 0
					response       = r[0]
					#check for relevant time key

					if 'ts' in response:
						
						ts                 = response['ts'] 
						elapsedTimeSeconds = time.time() - float( ts )
						
						if elapsedTimeSeconds < allowableTimeDeltaSeconds:

							if 'channel' in response and 'user' in response:
								#get the message
								text = ''
								if 'text' in response:
									text = response['text']

								replyText = handleText( text, response['channel'], response['user'] )

								if replyText:
									keepAliveCount = 0
									sendReply( sc, ts, response['channel'], replyText )
								else:
									logger.debug(  'replyText is empty!' )

							if 'channel' not in response:
								logger.debug(  'No Channel in response!' )

							if 'user' not in response:
								logger.debug(  'No user in response!' )

						else:
							logger.warn( 'ignoring stale response, elapsedTimeSeconds=' + str( timedelta( seconds=( elapsedTimeSeconds ) ) ) )

				if not r and keepAliveCount > maxKeepAlive:
					logger.info(  'Sleeping ' + str( sleepTimeSeconds ) + 's' )
					time.sleep( sleepTimeSeconds )
					keepAliveCount = 0
				else:
					time.sleep( 2 )
					keepAliveCount += 1

			except WebSocketConnectionClosedException:
				exc_type, exc_value, exc_tb = sys.exc_info()
				logger.warn( 'Caught WebSocketConnectionClosedException:' + str( "".join( traceback.format_exception( exc_type, exc_value, exc_tb ) ) ) )
				#try to re-connect
				sc.rtm_connect()

			except Exception as e:
				exc_type, exc_value, exc_tb = sys.exc_info()
				logger.error( 'Caught ' + str( "".join( traceback.format_exception( exc_type, exc_value, exc_tb ) ) ) )

		else:
			logger.error( "Connection Failed, invalid token?" )

	#todo try and post with sc "goodbye"

if __name__ == "__main__":
	main()