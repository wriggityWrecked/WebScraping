import datetime

class ScraperSchedule:

	#todo load schedule from a config file

	def __init__( self , scheduleDictionary ):
		#key, day of the week : value, hour in 24hr format
		#day of the week follows https://docs.python.org/2/library/datetime.html#datetime.datetime.weekday

		#todo need input validation
		#dict should look like this: {0:[1,12], 1:[2, 13],...}
		self.scheduleDictionary = scheduleDictionary

	def getScheduleForDay( self , desiredDayOfTheWeek ):
		
		if( desiredDayOfTheWeek < 0 or desiredDayOfTheWeek > 6 ):
			#todo just throw?
			return None, None, 'invalid ' + str( desiredDayOfTheWeek ) + ' specified: must be between 0-6'

		if desiredDayOfTheWeek not in self.scheduleDictionary:
			#todo just throw?
			return None, None, 'key ' + str( desiredDayOfTheWeek ) + ' not found'

		value = self.scheduleDictionary[ desiredDayOfTheWeek ]
		if len( value ) != 2:
			#todo just throw?
			return None, None, 'value malformed: unexpected length ' + str ( len ( value) ) + ', ' + str( value )

		return value[0], value[1], ""