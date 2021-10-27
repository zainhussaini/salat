from time import daylight
import salat
import datetime as dt
import math
import pytz


KAABAH_LONG_LAT = (39.8262, 21.4225)
EPOCH = dt.date(2021, 1, 1)
TIMEZONES = [
    dt.timezone.utc,
    dt.timezone(dt.timedelta(), "UTC"),
    dt.timezone(dt.timedelta(hours=3), "AST"),
    dt.timezone(dt.timedelta(hours=-5), "EST"),
    pytz.timezone("US/Eastern"),
]


def time_close(time1: dt.datetime, time2: dt.datetime, delta: dt.timedelta) -> bool:
    """Checks that two datetimes are within delta of each other

    Args:
        time1 (dt.datetime): first datetime
        time2 (dt.datetime): second datetime

    Returns:
        bool: True if both datetimes are within delta second of each other
    """
    if not math.isclose((time1 - time2).total_seconds(), 0, rel_tol=0, abs_tol=delta.total_seconds()):
        print(time1)
        print(time2)
        print(time1 - time2)
        return False
    else:
        return True


def parse_line(line: str, date: dt.date, timezone: dt.tzinfo):
    # line = "05:53 AM  06:58 AM  12:24 PM  03:29 PM  05:50 PM  06:56 PM"
    times = [a.strip() for a in line.split("  ")]

    hour_minute = []
    for time in times:
        h, mp = time.split(":")
        m, p = mp.split(" ")
        if p.upper() == "AM":
            hour = int(h)
            if h == "12":
                hour = 0
        elif p.upper() == "PM":
            hour = int(h) + 12
            if h == "12":
                hour = 12
        minute = int(m)
        hour_minute.append((hour, minute))
    assert len(hour_minute) == 6

    true_times = []
    for hour, minute in hour_minute:
        print(hour, minute)
        true_times.append(dt.datetime(date.year, date.month, date.day, hour, minute, tzinfo=timezone))
    assert len(true_times) == 6

    names = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
    return {names[i]: true_times[i] for i in range(6)}


def test_ISNA_Kaaba_epoch():
    long, lat = KAABAH_LONG_LAT
    calc_method = salat.CalculationMethod.ISNA
    asr_method = salat.AsrMethod.STANDARD
    date = EPOCH

    for tz in TIMEZONES:
        pt = salat.PrayerTimes(calc_method, asr_method)
        times = pt.calc_times(date, tz, long, lat)

        # https://www.islamicfinder.org/prayer-times/
        line = "05:53 AM   06:58 AM   12:24 PM   03:29 PM   05:50 PM   06:56 PM"
        timezone = dt.timezone(dt.timedelta(hours=3))
        true_times = parse_line(line, date, timezone)

        delta = dt.timedelta(minutes=1)
        for name in true_times:
            assert time_close(times[name], true_times[name], delta)


def test_MWL_Kaaba_epoch():
    long, lat = KAABAH_LONG_LAT
    calc_method = salat.CalculationMethod.MWL
    asr_method = salat.AsrMethod.STANDARD
    date = EPOCH

    for tz in TIMEZONES:
        pt = salat.PrayerTimes(calc_method, asr_method)
        times = pt.calc_times(date, tz, long, lat)

        # https://www.islamicfinder.org/prayer-times/
        line = "05:40 AM   06:58 AM   12:24 PM   03:29 PM   05:50 PM   07:05 PM"
        timezone = dt.timezone(dt.timedelta(hours=3))
        true_times = parse_line(line, date, timezone)

        delta = dt.timedelta(minutes=1)
        for name in true_times:
            assert time_close(times[name], true_times[name], delta)


# TODO:
# 1. check locations where sign if longitude and timezone offset are different (ie. long = -170, timezone= +12)
# 2. check daylight savings time transition points
# 4. check negative latitudes
# 3. check high latitudes