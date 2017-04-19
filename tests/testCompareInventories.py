import unittest

from utils import compareInventories

class TestCompareInventories( unittest.TestCase ):

	def test_inventoryFile2Dictionary( self ):
		d = compareInventories.inventoryFile2Dictionary( 'noFile.txt' )
		self.assertEqual( 0, len( d ) )

		d = compareInventories.inventoryFile2Dictionary( './tests/testData/emptyFile.txt' )
		self.assertEqual( 0, len( d ) )

		d = compareInventories.inventoryFile2Dictionary( \
			'./tests/testData/testDictionary1.json' )
		self.assertEqual( 2, len( d ) )
		self.assertTrue( 1 in d )
		self.assertTrue( 2 in d )
		self.assertEqual( 'foo', d[1] )
		self.assertEqual( 'bar', d[2] )

	def test_compareInventories( self ):
		r,n = compareInventories.compareInventories('./tests/testData/noFile.json',
	 		'./tests/testData/testDictionary2.json')
		self.assertEqual( {}, r )
		self.assertEqual( {}, n )

		r,n = compareInventories.compareInventories('./tests/testData/testDictionary2.json',
	 		'./tests/testData/noFile.json')
		self.assertEqual( {}, r )
		self.assertEqual( {}, n )

		r,n = compareInventories.compareInventories('./tests/testData/testDictionary1.json',
	 		'./tests/testData/testDictionary1.json')
		self.assertEqual( {}, r )
		self.assertEqual( {}, n )

		r,n = compareInventories.compareInventories('./tests/testData/testDictionary1.json',
			'./tests/testData/testDictionary2.json')
		self.assertEqual( {2 : 'bar'}, r )
		self.assertEqual( {3 : 'baz'}, n )

	def test_compareMap( self ):
		old  = {}
		new  = {}

		r, n = compareInventories.compareMap( old, new )
		self.assertEqual( old, r )
		self.assertEqual( new, n )

		old[42] = 'test'
		new[42] = 'test'

		r, n = compareInventories.compareMap( old, new )
		self.assertEqual( {}, r )
		self.assertEqual( {}, n )

		old[123] = 'removed'

		r, n = compareInventories.compareMap( old, new )
		self.assertEqual( {123 : 'removed'}, r )
		self.assertEqual( {}, n )

		new[321] = 'added'

		r, n = compareInventories.compareMap( old, new )	
		self.assertEqual( {123 : 'removed'}, r )
		self.assertEqual( {321 : 'added'}, n )

if __name__ == '__main__':
	unittest.main()