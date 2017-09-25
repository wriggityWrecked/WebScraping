"""Utility to provide a random user agent from a list of user agents given in
a file.

If called from the command line the main function will print the randomly
obtained user agent to stdout.

Example:
    $ python get_random_user_agent.py

"""

import logging
import os

from random import randint

USER_AGENT_FILE = os.path.join(os.path.dirname(__file__), './userAgentList.txt')
DEFAULT_USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
LOGGER = logging.getLogger(__name__)


def get_random_user_agent():
    """Function call to return a random user agent from the
    userAgentList file"""

    # does the file exist?
    if not os.path.isfile(USER_AGENT_FILE):
        logging.error(str(USER_AGENT_FILE) + ' not found!')
        return DEFAULT_USER_AGENT

    # todo get the upper bound from the file (line number)
    random_line_number = randint(1, 82)
    count = 0

    with open(USER_AGENT_FILE) as _file:
        for line in _file:
            if count == random_line_number:
                to_return = str(line.strip())
                logging.info('chose ' + to_return)
                return to_return
            else:
                count += 1

    logging.error('Unable to choose a random line! ' + str(random_line_number))
    return DEFAULT_USER_AGENT

if __name__ == '__main__':
    print(get_random_user_agent())
