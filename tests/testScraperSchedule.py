import unittest
from scraperSchedule import ScraperSchedule

class TestScraperSchedule(unittest.TestCase):

    def setUp( self ):
        schedule = { 1:[2,3], 5:[6,7] }
        self.scraperSchedule = ScraperSchedule( schedule )

    def test_badInput( self ):
        o,c,m = self.scraperSchedule.getScheduleForDay( 11 )
        self.assertEqual( o , None )
        self.assertEqual( c , None )

    def test_badKey( self ):
        o,c,m = self.scraperSchedule.getScheduleForDay( 4 )
        self.assertEqual( o , None )
        self.assertEqual( c , None )

    def test_expectedOutput(self):
        o,c,m = self.scraperSchedule.getScheduleForDay( 5 )
        self.assertEqual( o , 6 )
        self.assertEqual( c , 7 )

if __name__ == '__main__':
    unittest.main()