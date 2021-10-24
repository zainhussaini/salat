import salat
import datetime as dt
import math


def time_equals(time1: dt.datetime, time2: dt.datetime) -> bool:
    """Checks that two datetimes are within 1 microsecond of each other

    Args:
        time1 (dt.datetime): first datetime
        time2 (dt.datetime): second datetime

    Returns:
        bool: True if both datetimes are within 1 second of each other
    """
    if not math.isclose((time1 - time2).total_seconds(), 0, rel_tol=0, abs_tol=1e-6):
        print(time1)
        print(time2)
        print(time1 - time2)
        return False
    else:
        return True


def test_ISNA():
    pt = salat.PrayerTimes(salat.CalculationMethod.ISNA, salat.AsrMethod.STANDARD)

    # January 1, 2000
    date = dt.date(2000, 1, 1)

    # address of NYC
    longitude = -74.0060 # degrees East
    latitude = 40.7128 # degrees North

    # EST timezone (UTC offset of -5 hours)
    eastern = dt.timezone(dt.timedelta(hours=-5), "EST")

    prayer_times = pt.calc_times(date, eastern, longitude, latitude)

    fajr = dt.datetime(2000, 1, 1, 5, 58, 15, 232445, eastern)
    assert time_equals(prayer_times["fajr"], fajr)

    dhuhr = dt.datetime(2000, 1, 1, 11, 59, 25, 683315, eastern)
    assert time_equals(prayer_times["dhuhr"], dhuhr)

    asr = dt.datetime(2000, 1, 1, 14, 20, 54, 967648, eastern)
    assert time_equals(prayer_times["asr"], asr)

    maghrib = dt.datetime(2000, 1, 1, 16, 38, 42, 57867, eastern)
    assert time_equals(prayer_times["maghrib"], maghrib)

    isha = dt.datetime(2000, 1, 1, 18, 0, 36, 134185, eastern)
    assert time_equals(prayer_times["isha"], isha)

    midnight = dt.datetime(2000, 1, 1, 23, 59, 29, 74091, eastern)
    assert time_equals(prayer_times["midnight"], midnight)