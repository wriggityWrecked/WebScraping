"""Useful functions to compare inventory files.


This module provides functions to compare dictionaries or inventory files. It
can also be used as a script to compare inventory files via the command line.

Example:
    $ python compare_tools.py file1 file2

"""

import json
import sys
import filecmp
import os
import logging

from pprint import pprint


def hash_dict(dictionary):
    """
    Return the hashcode of the input dictionary. Useful for comparisons.
    """

    return hash(frozenset(dictionary))

def compare_map(old_map, new_map):
    """Compare two maps and return two maps, where the first map is contains
    all of the removed entries and the second contains all of the added
    entries.

    If no entries then empty maps will be returned or if the input maps' hashes
    are equal.
    """

    removed_entries = {}
    new_entries = {}

    #todo evauluate python sets
    #https://docs.python.org/2/library/sets.html
    #https://wiki.python.org/moin/TimeComplexity

    # check data hash, if equal no changes
    # frozenset is immutable, so can generate hash
    if hash_dict(old_map) == hash_dict(new_map):
        return removed_entries, new_entries

    for entry in new_map.keys():
        # check if in oldMap
        if entry not in old_map:
            new_entries[entry] = new_map[entry]

    for entry in old_map.keys():
        # check if in newMap
        if entry not in new_map:
            removed_entries[entry] = old_map[entry]

    return removed_entries, new_entries


def inventory_file_to_dictionary(inventory_file):
    """Convert an inventory file to a map. The inventory file must be JSON
    and have the following keys: name and id. An example is given as"

      [
      {"name": "Example Inventory Name", "id": 123456789},
      ...
      ]

    """

    dictionary = {}

    if not os.path.isfile(inventory_file):
        logging.error(str(inventory_file) + ' not found!')
        return dictionary

    if os.stat(inventory_file).st_size == 0:
        logging.error(str(inventory_file) + ' is empty!')
        return dictionary

    with open(inventory_file) as json_file:
        data = json.load(json_file)
        for line in data:
            # todo check that the line contains ID and NAME
            # if not then skip
            dictionary[line['id']] = line['name'].encode("utf8")

    return dictionary


def compare_inventory_files(inventory_file, new_file):
    """Compare two inventory files. Returns the removed and added entries
    by comparison via the compare_map function. Empty maps are returned in 
    error cases (file not found, file is empty) for more graceful handling
    upstream, rather than try / except."""

    removed = {}
    new = {}

    if not os.path.isfile(inventory_file):
        logging.error(str(inventory_file) + ' not found!')
        return removed, new

    if os.stat(inventory_file).st_size == 0:
        logging.error(str(inventory_file) + ' is empty!')
        return removed, new

    if not os.path.isfile(new_file):
        logging.error(str(new_file) + ' not found!')
        return removed, new

    if os.stat(new_file).st_size == 0:
        logging.error(str(new_file) + ' is empty!')
        return removed, new

    hash_map1 = inventory_file_to_dictionary(inventory_file)
    hash_map2 = inventory_file_to_dictionary(new_file)

    removed, new = compare_map(hash_map1, hash_map2)

    return removed, new


def dprint(removed, added):
    """Used for debug pretty printing two maps."""

    logging.info('')
    logging.info('')
    logging.info('Added:   ' + str(len(added)))
    logging.info('')
    logging.info(pprint(added))
    logging.info(
        '==================================================================')
    logging.info('Removed: ' + str(len(removed)))
    logging.info('')
    logging.info(pprint(removed))
    logging.info('')
    logging.info('')


def main():
    """Compare two inventory files provided as command line arguments. The
    output of the comparison is pretty printed."""

    # compare two inventory files
    if len(sys.argv) < 3:
        print 'must input two file names'
        return

    removed, new = compare_inventory_files(sys.argv[1], sys.argv[2])
    dprint(removed, new)


if __name__ == '__main__':
    main()
    