import logging

LOGGER = logging.getLogger(__name__)

ADDED_MAP_KEY = 'added_map'
REMOVED_MAP_KEY = 'removed_map'
DEFAULT_LINK_FORMATTER = lambda _id,_name: str(_name)
#add a method to convert all to string

#todo return a list rather than string for easier unit tests
def format_notification_message(results_dictionary, link_format_lambda=DEFAULT_LINK_FORMATTER):

    message = ''
    should_post = False
    added, removed = construct_notification_message(results_dictionary, link_format_lambda)
    added_number = len(added)
    removed_number = len(removed)

    if added_number > 0:
        message = 'Added : ' + str(added_number) + '\n\n'
        message += "\n".join(added)
        message += "\n"
        should_post = True

    if removed_number > 0 and len(removed) > 0:
        if len(message) > 0:
            message += '\n' + '-' * 25 + '\n\n'

        message += 'Removed : ' + str(removed_number) + '\n\n'
        message += "\n".join(removed)

    return should_post, message

def construct_notification_message(results_dictionary, link_format_lambda=DEFAULT_LINK_FORMATTER):
    
    # minimum results looks like
    #{"added_map": {}, "removed_map": {}}
    #where added_list / removed_list can look like: {"1": "A", "2": "B", "3": "C"} 
    
    added_map = {}
    removed_number = 0
    removed_map = {}

    constructed_added = []
    constructed_removed = []

    if ADDED_MAP_KEY in results_dictionary:
        added_map = results_dictionary[ADDED_MAP_KEY]

    added_number = len(added_map)

    if added_number > 0:
        constructed_added = construct_compared_message(added_number, added_map, link_format_lambda)

    if REMOVED_MAP_KEY in results_dictionary:
        removed_map = results_dictionary[REMOVED_MAP_KEY]

    removed_number = len(removed_map)

    if removed_number > 0:
        constructed_removed = construct_compared_message(removed_number, removed_map, link_format_lambda)

    return constructed_added, constructed_removed

def construct_compared_message(compared_number, compared_map, display_format_lambda=DEFAULT_LINK_FORMATTER):
    """
    todo document returned list
    todo document default lambda
    """

    message = []

    #sort the input list
    s = sorted(compared_map.items(), key=lambda x:x[1])
    for t in s:
        #index 1 is name, index 0 is ID
        message.append(display_format_lambda(str(t[0]),t[1]))
    return message

