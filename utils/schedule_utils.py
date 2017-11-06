import datetime
from random import uniform


def to_minutes(hours, minutes):
    """Return input in minutes.

    hours -- current hours to be converted
    minutes -- currents minutes added to converted hours
    """
    return hours * 60 + minutes


def get_current_day_hour_minute():
    """Return the current day, hour, minute from datetime.datetime.today().
    """
    today = datetime.datetime.today()
    return today.weekday(), today.hour, today.minute


def get_seconds_until_next_day():
    """Return the current day's hour and minutes and minutes.

    This is a helper function that simply takes the current hour, converts 
    it to minutes, adds and returns the current day's minutes.
    """
    _, hour, minute = get_current_day_hour_minute()
    return 24*60*60 - (hour*60*60 + minute*60)


def is_currently_schedulable(start_time_hour, end_time_hour): #hour minutes?
    
    day, hour, minute = get_current_day_hour_minute()
    current_minutes = to_minutes(hour, minute)
    
    start_time_minutes = to_minutes(start_time_hour, 0)
    end_time_minutes = to_minutes(end_time_hour, 0)

    return current_minutes >= start_time_minutes and current_minutes < end_time_minutes
