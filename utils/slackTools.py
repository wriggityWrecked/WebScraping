import os
import subprocess
from pprint import pprint

from slackclient import SlackClient

LOGGER = logging.getLogger(__name__)
TOKEN_FILE_PATH_AND_NAME = os.path.join(
    os.path.dirname(__file__), 'slackToken')

# so far link format only really works for prepend
# this belongs in scraper


def constructSlackMessageWithLink(resultsDictionary, linkFormat):

    # minimum looks like
    #{"addedLength": 0, "addedList": {}, "removedLength": 0, "removedList": {}}

    added = 0
    addedList = {}
    removed = 0
    removedList = {}
    message = ""
    ls = linkFormat

    if 'addedLength' in resultsDictionary and 'addedList' in resultsDictionary:
        added = int(resultsDictionary['addedLength'])
        addedList = resultsDictionary['addedList']

    #--- todo this should be a function
    if added > 0 and len(addedList) > 0:
        message = 'Added : ' + str(added) + '\n\n\n'

        if len(ls) > 0:
            # for now it's fine to append
            for t in addedList.items():
                message += str(t[1]) + " : " + ls + str(t[0]) + '\n\n'
        else:
            message += '\n\n'.join(' : '.join(t) for t in addedList.items())
    else:
        # nothing added, so don't construct a message
        return ''
    #--- end function

    if 'removedLength' in resultsDictionary and 'removedList' in resultsDictionary:
        removed = int(resultsDictionary['removedLength'])
        removedList = resultsDictionary['removedList']

    if removed > 0 and len(removedList) > 0:
        if len(message) > 0:
            message += '\n====================\n\n'

        message += 'Removed : ' + str(removed) + '\n\n\n'

        if len(ls) > 0:
            # for now it's fine to append
            for t in removedList.items():
                message += str(t[1]) + " : " + ls + str(t[0]) + '\n\n'
        else:
            message += '\n\n'.join(' : '.join(t) for t in removedList.items())

    return message


def constructSlackMessage(resultsDictionary):
    return constructSlackMessageWithLink(resultsDictionary, "")


def postMessage(channel, message):

    try:
        slackToken = ""
        with open(TOKEN_FILE_PATH_AND_NAME) as f:
            slackToken = str(f.read()).strip()

        sc = SlackClient(slackToken.strip())

        # check if token is empty
        if not sc:
            LOGGER.warn('Empty SlackToken!')
            return

        # check channel
        if not channel:
            LOGGER.warn('Empty channel!')
            return

        # check if message is empty
        if not message:
            LOGGER.warn('Empty message!')
            return

        output = sc.api_call(
            'chat.postMessage',
            channel='#' + channel,
            text=message
        )
        LOGGER.info(output)

    except Exception as _e:
        exc_type, exc_value, exec_tb = sys.exc_info()
        LOGGER.warn('Caught '
                    + str("".join(traceback.format_exception(
                        exc_type, exc_value, exec_tb))))


def postResultsToSlackChannelWithLink(resultsDictionary, linkFormat, channelName):

    message = constructSlackMessageWithLink(resultsDictionary, linkFormat)
    postMessage(channelName, message)


def postResultsToSlackChannel(resultsDictionary, channelName):

    message = constructSlackMessage(resultsDictionary)
    postMessage(channelName, message)


def test(fileName, linkFormat, channelName):

    rd = resultsFile2Dictionary(fileName)
    message = constructSlackMessage(rd)

    if len(message) > 0:
        print 'sending ' + message

    print '\n================\n\n'

    rd = resultsFile2Dictionary(fileName)
    message = constructSlackMessageWithLink(rd, linkFormat)

    if len(message) > 0:
        print 'sending ' + message
        postMessage(channelName, message)
