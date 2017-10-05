"""http://slackapi.github.io/python-slackclient/"""

import os
import subprocess
import logging
import threading
import sys
import logging
import traceback
import argparse

from multiprocessing import Queue
from Queue import Empty
from slackclient import SlackClient
from websocket import WebSocketConnectionClosedException

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))

TOKEN_FILE_PATH_AND_NAME = os.path.join(
    os.path.dirname(__file__), 'slackToken')

DEBUG_SLACK_CHANNEL = 'robot_comms'


class SlackPost(object):


    def __init__(self, channel, message):
        self.channel = channel
        self.message = message

    def __str__(self):
    	return 'channel=' + channel + ", message=" + message		

#https://docs.python.org/2/library/multiprocessing.html#exchanging-objects-between-processes
def run_slack_process(slack_token_path, queue):
	"""Call this as a process and daemon. Post message to slack via draining
	an input queue. """

	slack_token = "";

	queue.put(SlackPost("robot_comms", "yo yo yo i'm behanius rex"))

	with open(slack_token_path) as f:  
		slack_token = str(f.read()).strip()

	#if empty exit
	print slack_token
	sc = SlackClient(slack_token)

	if sc.rtm_connect():

		print sc.server

		while True:

			try:
				slack_post = queue.get() #block
				#this will throw in case we have an issue
				post_message_with_client(sc, slack_post.channel, slack_post.message)

			except Empty:
				print('empty')
				pass

			except WebSocketConnectionClosedException:
				exc_type, exc_value, exc_tb = sys.exc_info()
				LOGGER.warn( 'Caught WebSocketConnectionClosedException:' \
					+ str( "".join( traceback.format_exception( exc_type, exc_value, exc_tb ) ) ) )
				#try to re-connect
				sc.rtm_connect()

			except Exception as e:
				exc_type, exc_value, exc_tb = sys.exc_info()
				LOGGER.error( 'Caught ' + str( "".join( traceback.format_exception( exc_type, exc_value, exc_tb ) ) ) )

	else:
		LOGGER.error( "Connection Failed, invalid token?" )



def post_message(channel, message):
    """Post to slack given the input channel and message. This is simply a
    single operation that should not be shared between threads."""

    try:

        slack_token = ""
        with open(TOKEN_FILE_PATH_AND_NAME) as f:
            slack_token = str(f.read()).strip()

        sc = SlackClient(slack_token)

        # check if token is empty
        if not sc:
            LOGGER.warn('Empty slack_token: TOKEN_FILE_PATH_AND_NAME=' + str(TOKEN_FILE_PATH_AND_NAME))
            return False

        return post_message_with_client(sc, channel, message)

    except Exception as _e:
        exc_type, exc_value, exec_tb = sys.exc_info()
        LOGGER.warn('Caught '
                    + str("".join(traceback.format_exception(
                        exc_type, exc_value, exec_tb))))

#todo input token path

def post_message_with_client(slack_client, channel, message):

	# check channel
	if not channel:
	    LOGGER.warn('Empty channel!')
	    return False

	# check if message is empty
	if not message:
	    LOGGER.warn('Empty message!')
	    return False

	output = slack_client.api_call(
	    'chat.postMessage',
	    channel = '#' + channel,
	    text = message,
	    reply_broadcast = True
	)

	LOGGER.info(output)
	return True


def main():
    parser = argparse.ArgumentParser(
        description='Post to a slack channel given said channel and slack token')
    parser.add_argument('channel', metavar='Channel Name',
                        help='The channel in which to post a message')
    parser.add_argument('message', metavar='Message to Post',
                        help='The message to post to a slack channel')
    #todo optional token
    # parser.add_argument('--token', metavar='Slack Token File Path',
    #                     help='The path and name of the slack token for authentication')
    
    channel = parser.parse_args().channel
    message = parser.parse_args().message

    post_message(channel, message)


if __name__ == "__main__":
	main()
	