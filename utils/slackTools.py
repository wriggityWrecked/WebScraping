import os
import subprocess
import logging

from pprint import pprint
from compare_tools import inventory_file_to_dictionary
from slack_tools import post_message
from slackclient import SlackClient

LOGGER = logging.getLogger(__name__)

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

def postResultsToSlackChannelWithLink(resultsDictionary, linkFormat, channelName):

    message = constructSlackMessageWithLink(resultsDictionary, linkFormat)
    postMessage(channelName, message)


def postResultsToSlackChannel(resultsDictionary, channelName):

    message = constructSlackMessage(resultsDictionary)
    postMessage(channelName, message)


def test(fileName, linkFormat, channelName):

    rd = inventory_file_to_dictionary(fileName)
    message = constructSlackMessage(rd)

    if len(message) > 0:
        print 'sending ' + message

    print '\n================\n\n'

    rd = inventory_file_to_dictionary(fileName)
    message = constructSlackMessageWithLink(rd, linkFormat)

    if len(message) > 0:
        print 'sending ' + message
        postMessage(channelName, message)
