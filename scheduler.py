import threading
import datetime
import sched
import time
import datetime
import schedule

from random import uniform
from schedule import getHourMinuteIntsFromStringEntry

OPEN_MAX_PERIOD = 60 * 60
OPEN_MIN_PERIOD = 25 * 60
OPEN_DEFAULT_PERIOD = 40 * 60 #seconds
OPEN_MAX_DELAY = 20 * 60 #seconds

def getDayHourMinute():
	today = datetime.datetime.today()
	return today.weekday(), today.hour, today.minute

def calculateScheduleDelay(openEntry, closeEntry):

	global OPEN_MAX_PERIOD
	global OPEN_MIN_PERIOD
	global OPEN_DEFAULT_PERIOD
	global OPEN_MAX_DELAY

	#THIS IS NOT UTC
	day, hour, minute = getDayHourMinute()

	# if peakStartEntry not None and peakEndEntry not None:
	# 	#is it peak hours?
	# 	peakStartHour, peakStartMinute = scraperSchedule.getHourMinuteIntsFromStringEntry( peakStartEntry )
	# 	peakEndHour, peakEndMinute = scraperSchedule.getHourMinuteIntsFromStringEntry( peakEndEntry )

	# 	if psh < hour and psm < minute and hour < peh and minute < pem:
	# 		#we are in a peak time

	#todo peak times
	openHour, openMinute = getMinutesFromStringEntry( openEntry )
	closeHour, closeMinute = getMinutesFromStringEntry( closeEntry )

	print openHour
	print closeHour
	print hour
	if hour >= openHour and hour < closeHour and minute >= openMinute:
		#open for business, go ahead and scrape
		delaySeconds = OPEN_DEFAULT_PERIOD + uniform(-1*OPEN_MAX_DELAY, OPEN_MAX_DELAY)
		print delaySeconds
		delaySeconds = max(delaySeconds, OPEN_MIN_PERIOD)
		print delaySeconds
		delaySeconds = min(delaySeconds, OPEN_MAX_PERIOD)

		print str(delaySeconds)
		return delaySeconds

	#we can't run right now! need to delay until the next day opening
	return -1

class Scheduler:

	def __init__( self, Scraper, scheduleDictionary ):

		self.schedule        = Schedule( scheduleDictionary )
		self.scraper         = Scraper
		self.scheduler       = sched.scheduler( time.time, time.sleep )
		self.events          = {}
		self.timeLastRan     = 0

	def getEnteredScheduleForDay(self, day):
		#get the entry from the dictionary
		openEntry, closeEntry, peakStartEntry, peakEndEntry, message = self.scraperSchedule.getScheduleForDay( day )

		if openEntry is None or closeEntry is None:
			#can't schedule, need to wait until the next day
			return self.calculateScheduleDelay( self.scraperSchedule.getScheduleForDay( day + 1 ) ) 

		return openEntry, closeEntry, peakStartEntry, peakEndEntry, message





def printHi():
	print 'hi ' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def main():

	s = sched.scheduler( time.time, time.sleep )

	s.enter( 1, 1, printHi, () )
	s.enter( 2, 2, printHi, () )

	print str( s.queue )

	s.run()

	print 'done'
	s.enter( 2, 2, printHi, () )
	print str( s.queue )
	s.run()

if __name__ == "__main__":
	main()