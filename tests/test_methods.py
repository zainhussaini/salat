import salat
import datetime as dt
import math


def within_second(time1: dt.datetime, time2: dt.datetime) -> bool:
    """Checks that two datetimes are within 1 second of each other

    Args:
        time1 (dt.datetime): first datetime
        time2 (dt.datetime): second datetime

    Returns:
        bool: True if both datetimes are within 1 second of each other
    """
    if not math.isclose((time1 - time2).total_seconds(), 0, rel_tol=0, abs_tol=1):
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

    # EST timezone (UTC offset of -5) on date
    eastern = dt.timezone(dt.timedelta(hours=-4))

    prayer_times = pt.calc_times(date, eastern, longitude, latitude)

    fajr = dt.datetime(2000, 1, 1, 6, 58, 14, tzinfo=eastern)
    assert within_second(prayer_times["fajr"], fajr)

    dhuhr = dt.datetime(2000, 1, 1, 12, 59, 24, tzinfo=eastern)
    assert within_second(prayer_times["dhuhr"], dhuhr)

    asr = dt.datetime(2000, 1, 1, 15, 20, 53, tzinfo=eastern)
    assert within_second(prayer_times["asr"], asr)

    maghrib = dt.datetime(2000, 1, 1, 17, 38, 40, tzinfo=eastern)
    assert within_second(prayer_times["maghrib"], maghrib)

    isha = dt.datetime(2000, 1, 1, 19, 0, 34, tzinfo=eastern)
    assert within_second(prayer_times["isha"], isha)

    midnight = dt.datetime(2000, 1, 2, 0, 59, 27, tzinfo=eastern)
    assert within_second(prayer_times["midnight"], midnight)