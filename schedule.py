import datetime
from random import uniform

NORMAL_HOURS_KEY = 'n'
PEAK_HOURS_KEY = 'p'
OPEN_MAX_PERIOD_MINUTES = 60
OPEN_MIN_PERIOD_MINUTES = 25
OPEN_DEFAULT_PERIOD_MINUTES = 42
OPEN_MAX_DELAY_MINUTES = 20


def validateScheduleDictionary(dictionaryToValidate):
    # check all the keys
    if dictionaryToValidate is None or not dictionaryToValidate:
        return False, "input cannot be empty!"


def getMinutesFromStringEntry(stringEntry):

    if not stringEntry:
        return None

    split = stringEntry.split(':')

    if len(split) == 1:
        return int(split[0]) * 60
    elif len(split) == 2:
        return int(split[0]) * 60 + int(split[1])

        # key, day of the week : value, hour in 24hr format
        # day of the week follows
        # https://docs.python.org/2/library/datetime.html#datetime.datetime.weekday

        # todo need input validation
        # dict should look like this: { 0: {'n' : ['1','12'], 'p' : ['10:30',
        # '14:30'] }, ... }

        #{0: {'operating': [8, 20], 'peak': [11, 4]}}

        # toto validate before settings


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

    o = subDictionary[NORMAL_HOURS_KEY][0]
    c = subDictionary[NORMAL_HOURS_KEY][1]

    ps = None
    pe = None

    if PEAK_HOURS_KEY in subDictionary:
        ps = subDictionary[PEAK_HOURS_KEY][0]
        pe = subDictionary[PEAK_HOURS_KEY][1]

    return o, c, ps, pe, ""


def getCurrentDayHourMinute():

    today = datetime.datetime.today()
    return today.weekday(), today.hour, today.minute


def calculateScheduleDelay(openMinutes, closeMinutes):

    # THIS IS NOT UTC
    day, hour, minute = getCurrentDayHourMinute()

    currentMinutes = (hour * 60) + minute

    if currentMinutes >= openMinutes and currentMinutes < closeMinutes:
        # open for business, go ahead and scrape
        delaySeconds = OPEN_DEFAULT_PERIOD_MINUTES * 60 + \
            uniform(-1 * OPEN_MAX_DELAY_MINUTES *
                    60, OPEN_MAX_DELAY_MINUTES * 60)
        delaySeconds = max(delaySeconds, OPEN_MIN_PERIOD_MINUTES * 60)
        delaySeconds = min(delaySeconds, OPEN_MAX_PERIOD_MINUTES * 60)

        return delaySeconds

    # we can't run right now! need to delay until the next day opening
    return -1  # todo something better than -1?
