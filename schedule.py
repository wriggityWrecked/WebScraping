import datetime
from random import uniform

NORMAL_HOURS_KEY = 'n'
PEAK_HOURS_KEY = 'p'

NORMAL_MAX_PERIOD_MINUTES = 60
NORMAL_MIN_PERIOD_MINUTES = 20
NORMAL_DEFAULT_PERIOD_MINUTES = 40
NORMAL_MAX_DELAY_MINUTES = 20

PEAK_MAX_PERIOD_MINUTES = 35
PEAK_MIN_PERIOD_MINUTES = 15
PEAK_DEFAULT_PERIOD_MINUTES = 25
PEAK_MAX_DELAY_MINUTES = 10

#todo this should probably be a class


# def validateScheduleDictionary(dictionaryToValidate):
    
#     if dictionaryToValidate is None or not dictionaryToValidate:
#         return False, 'input cannot be empty!'

#     #check all the keys
#     for key, value in dictionaryToValidate.iteritems():
#     	if key < 0 or key > 6:
#     		return False, 'invalid input key: ' + str(key) + ', must be [0,6]'
#     		#value should be a map
#     		if

def to_minutes(hours, minutes):
    """Return input in minutes.

    hours -- current hours to be converted
    minutes -- currents minutes added to converted hours
    """
    return hours * 60 + minutes

#todo need to return as a tuple, so to determine if open is somethin like
#23:30 and close is the next day at 12
def getMinutesFromStringEntry(string_entry):
    """
    """

    if not string_entry:
        return None

    split = string_entry.split(':')

    if len(split) == 1:
        return to_minutes(int(split[0]), 0)
    elif len(split) == 2:
        return to_minutes(int(split[0]), int(split[1]))

        # key, day of the week : value, hour in 24hr format
        # day of the week follows
        # https://docs.python.org/2/library/datetime.html#datetime.datetime.weekday

        # todo need input validation
        # dict should look like this: { 0: {'n' : ['1','12'], 'p' : ['10:30',
        # '14:30'] }, ... }

        #{0: {'operating': [8, 20], 'peak': [11, 4]}}

        # toto validate before settings

def getScheduleForDayInMinutes(scheduleDictionary, desiredDayOfTheWeek):

    open_, close_, peak_start, peak_end, message = getScheduleForDay(scheduleDictionary, desiredDayOfTheWeek)

    if open_ != None:
        return getMinutesFromStringEntry(open_), getMinutesFromStringEntry(close_), \
                getMinutesFromStringEntry(peak_start), getMinutesFromStringEntry(peak_end), message

    return None, None, None, None, "none"

def getScheduleForDay(scheduleDictionary, desiredDayOfTheWeek):

    if desiredDayOfTheWeek < 0 or desiredDayOfTheWeek > 6:
        # todo just throw?
        return None, None, None, None, 'invalid ' + str(desiredDayOfTheWeek) \
            + ' specified: must be between 0-6'

    if desiredDayOfTheWeek not in scheduleDictionary:
        # todo just throw?
        return None, None, None, None, 'key ' + str(desiredDayOfTheWeek) + ' not found'

    subDictionary = scheduleDictionary[desiredDayOfTheWeek]

    if len(subDictionary) < 1:
        # todo just throw?
        return None, None, None, None, 'value malformed: unexpected length ' \
            + str(len(subDictionary)) + ', ' + str(subDictionary)

    if NORMAL_HOURS_KEY not in subDictionary:
        return None, None, None, None, 'normalHoursKey ' + NORMAL_HOURS_KEY + \
            ' not found ' + str(subDictionary)

    open_ = subDictionary[NORMAL_HOURS_KEY][0]
    close_ = subDictionary[NORMAL_HOURS_KEY][1]

    peak_start = None
    peak_end = None

    if PEAK_HOURS_KEY in subDictionary:
        peak_start = subDictionary[PEAK_HOURS_KEY][0]
        peak_end = subDictionary[PEAK_HOURS_KEY][1]

    return open_, close_, peak_start, peak_end, ""


def getCurrentDayHourMinute():
    """Return the current day, hour, minute from datetime.datetime.today().
    """
    today = datetime.datetime.today()
    return today.weekday(), today.hour, today.minute


def getSecondsUntilNextDay():
    """Return the current day's hour and minutes and minutes.

    This is a helper function that simply takes the current hour, converts 
    it to minutes, adds and returns the current day's minutes.
    """
    _, hour, minute = getCurrentDayHourMinute()
    return 24*60*60 - (hour*60*60 + minute*60)


def isCurrentlyScheduleable(scheduleDictionary, day):

    #these are in minutes
    open_, close_, peak_start, peak_end, _ = getScheduleForDayInMinutes(scheduleDictionary, day)
    
    day, hour, minute = getCurrentDayHourMinute()
    current_minutes = to_minutes(hour, minute)

    return current_minutes >= peak_start and current_minutes < peak_end or \
            current_minutes >= open_ and current_minutes < close_


def getScheduleDelayForDay(scheduleDictionary, inputDay):
    """Return the current schedule of the specified day. 

    Args: 
        scheduleDictionary: dictionary representing a valid schedule. 
        day: day desired to extract from dictionary. 
    """
    #these are in minutes
    open_, close_, peak_start, peak_end, _ = getScheduleForDayInMinutes(scheduleDictionary, inputDay)
    
    day, hour, minute = getCurrentDayHourMinute()
    current_minutes = to_minutes(hour, minute)

    if current_minutes >= peak_start and current_minutes < peak_end:
        return calculateScheduleDelay(True)
    elif current_minutes >= open_ and current_minutes < close_:
        return calculateScheduleDelay(False)
    else:
        return -1


def calculateScheduleDelay(is_peak):

    if is_peak:
        period_minutes = PEAK_DEFAULT_PERIOD_MINUTES
        min_period_minutes = PEAK_MIN_PERIOD_MINUTES
        max_period_minutes = PEAK_MAX_PERIOD_MINUTES
        max_delay_minutes = PEAK_MAX_DELAY_MINUTES
    else:
        period_minutes = NORMAL_DEFAULT_PERIOD_MINUTES
        min_period_minutes = NORMAL_MIN_PERIOD_MINUTES
        max_period_minutes = NORMAL_MAX_PERIOD_MINUTES
        max_delay_minutes = NORMAL_MAX_DELAY_MINUTES

    delay_seconds = period_minutes * 60 + \
        uniform(-1 * max_delay_minutes *
                60, max_delay_minutes * 60)
    delay_seconds = max(delay_seconds, min_period_minutes * 60)
    delay_seconds = min(delay_seconds, max_period_minutes * 60)

    return delay_seconds
