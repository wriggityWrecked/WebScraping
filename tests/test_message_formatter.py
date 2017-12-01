"""Tests for the message_formatter module."""

import unittest

from utils import message_formatter 


class TestMessageFormatter(unittest.TestCase):


    def test_construct_compared_message(self):
        
        test_dict = {"1": "A", "2": "B", "3": "C"}
        link = 'http://test/'
        
        #test with custom lambda
        output = message_formatter.construct_compared_message(len(test_dict), \
            test_dict, lambda _id,_name: _name + " : " + link + _id)

        i = 0
        for key, value in test_dict.iteritems():
            self.assertEqual(value + ' : ' + link + key, output[i])
            i += 1

        #test with default lamba
        output = message_formatter.construct_compared_message(len(test_dict), test_dict)

        i = 0
        for key, value in test_dict.iteritems():
            self.assertEqual(value + ' : ' + key, output[i])
            i += 1


    def test_construct_notification_message(self):

        test_dict = {message_formatter.ADDED_MAP_KEY: {"1": "A", "2": "B"},\
            message_formatter.REMOVED_MAP_KEY: {"26" : "Z"}}

        added, removed = message_formatter.construct_notification_message(test_dict)

        self.assertEqual('A : 1', added[0])
        self.assertEqual('B : 2', added[1])
        self.assertEqual('Z : 26', removed[0])

        print "\n\n"
        print message_formatter.format_notification_message(test_dict)
        

if __name__ == '__main__':
    unittest.main()
