from slackclient import SlackClient
from datetime    import timedelta
from subprocess  import *
from websocket   import *
import time
import traceback
import sys
import scrapeKnl
import scrapeEtre
import threading

commandKey        = 'bash'
commandChannel    = 'C4UC35TLN'
dbId              = 'U4SDBCXBJ'
debugSlackChannel = 'robot_comms'
scrapeKey         = 'scrape'
knlScrapeKey      = 'knl'
etreScrapeKey     = 'etre'
#todo help key / list commands

#todo need logging

#todo global thread dictionary to keep track of manual scrapes

def handleText( text, channel, user ):

	print 'handleText: ' + text + ' ' + channel + ' ' + user

	if not text:
		print 'ignoring empty message'
		return ''

	if 'who knows' in text:
		return 'Jeff knows.'

	#split on spaces and grab the first word
	key = text.split(" ")
	if  len( key ) == 0:
		print 'empty key!'
		return ''

	key = key[0]
	print key
	#handle scraping
	if key.lower() == scrapeKey.lower():
		
		return handleScrape( text.replace( scrapeKey + " ", "" ) )

	#handle commands
	if key.lower() == commandKey.lower():

		return handleCommand( text.replace( commandKey + " ", "" ) )

	return ''

def handleCommand( command ):
	print 'handleCommand: ' + str( command )

	try:

		p              = Popen( command, shell=True, stdout=PIPE )
		stdout, stderr = p.communicate()
		
		print stdout
		print stderr

		return str( stdout ) + '\n' + str( stderr )

	except Exception as e:
		exc_type, exc_value, tb = sys.exc_info()
		return False, 'Caught ' + str( traceback.format_exception( exc_type, exc_value, tb ) ) 

def handleScrape( command ):

	print 'handleScrape: ' + command

	if command.lower() == knlScrapeKey.lower():

		t = threading.Thread( target=scrapeKnl.main, args=() )
		t.daemon = True
		t.start()

		return 'Acknowledged command, started manual KnL scraping'

	if command.lower() == etreScrapeKey.lower():

		t = threading.Thread( target=scrapeEtre.main, args=() )
		t.daemon = True
		t.start()

		return 'Acknowledged command, started manual Etre scraping'


def sendReply( sc, ts, channelId, replyText ):

	print ts + ' ' + channelId + ' ' + replyText

	output = sc.api_call(
	  'chat.postMessage',
	  ts         = ts,
	  channel    = channelId,
	  text       = replyText
	)
	print output

def main():

	sleepTimeSeconds          = 60
	allowableTimeDeltaSeconds = 3 * sleepTimeSeconds
	slackToken                = "";

	with open( './slackToken' ) as f:  
		slackToken = str( f.read() ).strip()

	sc = SlackClient( slackToken.strip() )

	if sc.rtm_connect():

		keepAliveCount = 0

		while True:

			try:

				r = sc.rtm_read()
				print str( time.time() ) + ' ' + str( r )

				#check time, if it's the time delta is greater than our polling then       
				if len( r ) > 0:
					attemptCount = 0
					response     = r[0]
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
									sendReply( sc, ts, response['channel'], replyText )
								else:
									print 'replyText is empty!'

							if 'channel' not in response:
								print 'No Channel in response!'

							if 'user' not in response:
								print 'No user in response!'

						else:
							print 'ignoring stale response, elapsedTimeSeconds=' + str( timedelta( seconds=( elapsedTimeSeconds ) ) )

				if not r and keepAliveCount > 10:
					time.sleep( sleepTimeSeconds )
					keepAliveCount = 0
				else:
					time.sleep( 1 )
					keepAliveCount += 1

			except WebSocketConnectionClosedException:
				exc_type, exc_value, tb = sys.exc_info()
				print 'Caught ' + str( traceback.format_exception( exc_type, exc_value, tb ) )
				#try to re-connect
				sc.rtm_connect()

			except Exception as e:
				exc_type, exc_value, tb = sys.exc_info()
				print 'Caught ' + str( traceback.format_exception( exc_type, exc_value, tb ) ) 

		else:
			print "Connection Failed, invalid token?"

if __name__ == "__main__":
	main()

#[{u'type': u'user_typing', u'user': u'U4SDBCXBJ', u'channel': u'C4UC35TLN'}]
#[]
#[{u'source_team': u'T4T2PLK19', u'text': u'ok this is kind of cool', u'ts': u'1491258110.542624', u'user': u'U4SDBCXBJ', u'team': u'T4T2PLK19', u'type': u'message', u'channel': u'C4UC35TLN'}]
#[{u'source_team': u'T4T2PLK19', u'text': u'<@U4SEQN397> yoyoyo', u'ts': u'1491258170.557648', u'user': u'U4SDBCXBJ', u'team': u'T4T2PLK19', u'type': u'message', u'channel': u'C4UC35TLN'}]
#[{u'launchUri': u'slack://channel?id=C4UC35TLN&message=1491258170557648&team=T4T2PLK19', u'subtitle': u'#botinfo', u'is_shared': False, u'title': u'B33R', u'ssbFilename': u'knock_brush.mp3', u'avatarImage': u'https://avatars.slack-edge.com/2017-04-01/162507456977_33a4b8e55a017b9db5b6_192.png', u'imageUri': None, u'content': u'devin: @b33rscraper yoyoyo', u'event_ts': u'1491258170.101887', u'msg': u'1491258170.557648', u'type': u'desktop_notification', u'channel': u'C4UC35TLN'}]

# [{u'name': u'robot_comms', u'user_profile': {u'avatar_hash': u'33a4b8e55a01', u'first_name': u'Devin', u'real_name': u'Devin Bonnie', u'name': u'devin', u'image_72': u'https://avatars.slack-edge.com/2017-04-01/162507456977_33a4b8e55a017b9db5b6_72.png'}, u'event_ts': u'1491258893.728737', u'text': u'<@U4SDBCXBJ|devin> has renamed the channel from "botinfo" to "robot_comms"', u'team': u'T4T2PLK19', u'ts': u'1491258893.728737', u'subtype': u'channel_name', u'user': u'U4SDBCXBJ', u'old_name': u'botinfo', u'type': u'message', u'channel': u'C4UC35TLN'}]
# [{u'event_ts': u'1491258893.689734', u'type': u'channel_rename', u'channel': {u'created': u'1491238543', u'id': u'C4UC35TLN', u'is_channel': True, u'name': u'robot_comms'}}]
# [{u'url': u'wss://mpmulti-mgmw.slack-msgs.com/websocket/IjHTJT2QPyeLuncfA0eFsL-_RmNobcd_D0fXM0BjT8XBoGXBXxsS_r-Jnis7KUboY-wSc0sxOfMNCNZ5ifwYknhMJ0bujd5NEKj2mGRja9bCDU7EV3kZa1mYSQniK1M_fTTN6hd6qcsQngqc_vSH0jp5v87hTgZJWbs3OpvMbDQ=', u'type': u'reconnect_url'}]
# [{u'type': u'presence_change', u'user': u'U4SEQN397', u'presence': u'active'}]
# [{u'type': u'user_typing', u'user': u'U4SDBCXBJ', u'channel': u'C4UC35TLN'}]
# [{u'source_team': u'T4T2PLK19', u'text': u'asdf', u'ts': u'1491258951.742096', u'user': u'U4SDBCXBJ', u'team': u'T4T2PLK19', u'type': u'message', u'channel': u'C4UC35TLN'}]
# [{u'type': u'user_typing', u'user': u'U4SDBCXBJ', u'channel': u'C4UC35TLN'}]
# [{u'type': u'user_typing', u'user': u'U4SDBCXBJ', u'channel': u'C4UC35TLN'}]
# [{u'type': u'user_typing', u'user': u'U4SDBCXBJ', u'channel': u'C4UC35TLN'}]
# [{u'source_team': u'T4T2PLK19', u'text': u'<@U4SEQN397> fdas', u'ts': u'1491258957.743578', u'user': u'U4SDBCXBJ', u'team': u'T4T2PLK19', u'type': u'message', u'channel': u'C4UC35TLN'}]
# [{u'launchUri': u'slack://channel?id=C4UC35TLN&message=1491258957743578&team=T4T2PLK19', u'subtitle': u'#robot_comms', u'is_shared': False, u'title': u'B33R', u'ssbFilename': u'knock_brush.mp3', u'avatarImage': u'https://avatars.slack-edge.com/2017-04-01/162507456977_33a4b8e55a017b9db5b6_192.png', u'imageUri': None, u'content': u'devin: @b33rscraper fdas', u'event_ts': u'1491258957.316085', u'msg': u'1491258957.743578', u'type': u'desktop_notification', u'channel': u'C4UC35TLN'}]
