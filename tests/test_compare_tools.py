"""Tests for the compare_tools module."""

import unittest

from utils import compare_tools


class TestCompareInventories(unittest.TestCase):


    def test_inventory_file_to_dictionary(self):

        d = compare_tools.inventory_file_to_dictionary('noFile.txt')
        self.assertEqual(0, len(d))

        d = compare_tools.inventory_file_to_dictionary(
            './tests/testData/emptyFile.txt')
        self.assertEqual(0, len(d))

        d = compare_tools.inventory_file_to_dictionary(
            './tests/testData/testDictionary1.json')
        self.assertEqual(2, len(d))
        self.assertTrue(1 in d)
        self.assertTrue(2 in d)
        self.assertEqual('foo', d[1])
        self.assertEqual('bar', d[2])

    def test_compare_inventories(self):

        r, n = compare_tools.compare_inventory_files('./tests/testData/noFile.json',
                                                     './tests/testData/testDictionary2.json')
        self.assertEqual({}, r)
        self.assertEqual({}, n)

        r, n = compare_tools.compare_inventory_files('./tests/testData/testDictionary2.json',
                                                     './tests/testData/noFile.json')
        self.assertEqual({}, r)
        self.assertEqual({}, n)

        r, n = compare_tools.compare_inventory_files('./tests/testData/testDictionary1.json',
                                                     './tests/testData/testDictionary1.json')
        self.assertEqual({}, r)
        self.assertEqual({}, n)

        r, n = compare_tools.compare_inventory_files('./tests/testData/testDictionary1.json',
                                                     './tests/testData/testDictionary2.json')
        self.assertEqual({2: 'bar'}, r)
        self.assertEqual({3: 'baz'}, n)

    def test_compare_map(self):
    	
        old = {}
        new = {}

        r, n = compare_tools.compare_map(old, new)
        self.assertEqual(old, r)
        self.assertEqual(new, n)

        old[42] = 'test'
        new[42] = 'test'

        r, n = compare_tools.compare_map(old, new)
        self.assertEqual({}, r)
        self.assertEqual({}, n)

        old[123] = 'removed'

        r, n = compare_tools.compare_map(old, new)
        self.assertEqual({123: 'removed'}, r)
        self.assertEqual({}, n)

        new[321] = 'added'

        r, n = compare_tools.compare_map(old, new)
        self.assertEqual({123: 'removed'}, r)
        self.assertEqual({321: 'added'}, n)


if __name__ == '__main__':
    unittest.main()
