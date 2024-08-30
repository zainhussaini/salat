import salat
import datetime as dt
import math
import pytz


KAABAH_LAT_LONG = (21.422487, 39.826206)
EMPIRE_STATE_BUILDING_LAT_LONG = (40.748817, -73.985428)
EPOCH_DATE = dt.date(2000, 1, 1)
DEFAULT_TIME_CLOSE_DELTA_MINS = 1


def output_correct(
    times: "dict[str, dt.datetime]",
    true_times: "dict[str, dt.datetime]",
    delta: dt.timedelta = None,
) -> bool:
    """Checks that two output lists represent the same times"""
    if delta is None:
        delta = dt.timedelta(minutes=DEFAULT_TIME_CLOSE_DELTA_MINS)

    assert times.keys() == true_times.keys()

    for name in times:
        time = times[name]
        true_time = true_times[name]
        assert math.isclose(
            (time - true_time).total_seconds(),
            0,
            rel_tol=0,
            abs_tol=delta.total_seconds(),
        )


def output_timezone_correct(times: "dict[str, dt.datetime]", timezone: dt.timezone):
    for name, time in times.items():
        assert time.tzinfo is not None
        assert time.utcoffset() == timezone.utcoffset(time.replace(tzinfo=None))


def parse_line(
    line: str, date: dt.date, timezone: dt.tzinfo
) -> "dict[str, dt.datetime]":
    """Converts string of times to package output format for direct comparison"""
    # example line: "05:53 AM  06:58 AM  12:24 PM  03:29 PM  05:50 PM  06:56 PM"
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
        if hasattr(timezone, "localize"):
            true_time = timezone.localize(
                dt.datetime(date.year, date.month, date.day, hour, minute)
            )
        else:
            true_time = dt.datetime(
                date.year, date.month, date.day, hour, minute, tzinfo=timezone
            )
        true_times.append(true_time)
    assert len(true_times) == 6

    names = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
    return {names[i]: true_times[i] for i in range(6)}


def test_parse_lines1():
    """Tests that parse_line function works correctly by converting and converting back"""
    line = "05:53 AM   06:58 AM   12:24 PM   03:29 PM   05:50 PM   06:56 PM"
    date = dt.date(1970, 1, 1)
    timezone = dt.timezone(dt.timedelta(hours=-5), "EST")

    true_times = parse_line(line, date, timezone)
    line_from_true_times = "   ".join(true_times[name].strftime("%I:%M %p") for name in true_times)
    assert line == line_from_true_times


def test_parse_lines2():
    """Same as test_parse_lines1 except with pytz timezone"""
    line = "05:53 AM   06:58 AM   12:24 PM   03:29 PM   05:50 PM   06:56 PM"
    date = dt.date(1970, 1, 1)
    timezone = pytz.timezone("US/Eastern")

    true_times = parse_line(line, date, timezone)
    line_from_true_times = "   ".join(true_times[name].strftime("%I:%M %p") for name in true_times)
    assert line == line_from_true_times


def test1():
    # https://www.islamicfinder.org/prayer-times/
    line = "05:59 AM   07:20 AM   12:00 PM   02:21 PM   04:39 PM   06:01 PM"

    lat, long = EMPIRE_STATE_BUILDING_LAT_LONG
    date = EPOCH_DATE
    timezone = dt.timezone(dt.timedelta(hours=-5), "EST")
    calc_method = salat.CalculationMethod.ISNA
    asr_method = salat.AsrMethod.STANDARD

    pt = salat.PrayerTimes(calc_method, asr_method)
    times = pt.calc_times(date, timezone, long, lat)
    true_times = parse_line(line, date, timezone)

    output_correct(times, true_times)
    output_timezone_correct(times, timezone)


def test2():
    # https://www.islamicfinder.org/prayer-times/
    line = "05:40 AM   06:58 AM   12:24 PM   03:29 PM   05:50 PM   07:05 PM"

    lat, long = KAABAH_LAT_LONG
    date = EPOCH_DATE
    timezone = pytz.timezone("Asia/Riyadh")
    calc_method = salat.CalculationMethod.MWL
    asr_method = salat.AsrMethod.STANDARD

    pt = salat.PrayerTimes(calc_method, asr_method)
    times = pt.calc_times(date, timezone, long, lat)
    true_times = parse_line(line, date, timezone)

    output_correct(times, true_times)
    output_timezone_correct(times, timezone)


def test3():
    # https://www.islamicfinder.org/prayer-times/
    line = "05:37 AM   06:58 AM   12:24 PM   03:29 PM   05:50 PM   07:50 PM"

    lat, long = KAABAH_LAT_LONG
    date = EPOCH_DATE
    timezone = dt.timezone(dt.timedelta(hours=3), "AST")
    calc_method = salat.CalculationMethod.MAKKAH
    asr_method = salat.AsrMethod.STANDARD

    pt = salat.PrayerTimes(calc_method, asr_method)
    times = pt.calc_times(date, timezone, long, lat)
    true_times = parse_line(line, date, timezone)

    output_correct(times, true_times)
    output_timezone_correct(times, timezone)


def test4():
    # https://www.islamicfinder.org/prayer-times/
    line = "05:41 AM  06:59 AM  12:34 PM  03:46 PM  06:09 PM  07:39 PM"

    lat, long = KAABAH_LAT_LONG
    date = dt.date(2000, 1, 30)
    timezone = pytz.timezone("Asia/Riyadh")
    calc_method = salat.CalculationMethod.MAKKAH
    asr_method = salat.AsrMethod.STANDARD

    pt = salat.PrayerTimes(calc_method, asr_method)
    times = pt.calc_times(date, timezone, long, lat)
    true_times = parse_line(line, date, timezone)

    output_correct(times, true_times)
    output_timezone_correct(times, timezone)


def test5():
    # https://www.islamicfinder.org/prayer-times/
    # Note: this website does not adjust Maghrib angle correctly, so the output was adjusted
    # manually
    line = "05:49 AM  06:58 AM  12:24 PM  03:29 PM  06:04 PM  06:51 PM"

    lat, long = KAABAH_LAT_LONG
    date = EPOCH_DATE
    timezone = pytz.timezone("Asia/Riyadh")
    calc_method = salat.CalculationMethod.JAFARI
    asr_method = salat.AsrMethod.STANDARD

    pt = salat.PrayerTimes(calc_method, asr_method)
    times = pt.calc_times(date, timezone, long, lat)
    true_times = parse_line(line, date, timezone)

    output_correct(times, true_times)
    output_timezone_correct(times, timezone)


def test6():
    # https://www.islamicfinder.org/prayer-times/
    line = "04:45 AM   05:58 AM   11:52 AM   03:14 PM   05:46 PM   06:55 PM"

    lat, long = -6.6432601, 106.1872718
    date = dt.date(2023, 5, 22)
    timezone = pytz.timezone("Asia/Jakarta")
    calc_method = salat.CalculationMethod.MWL
    asr_method = salat.AsrMethod.STANDARD

    pt = salat.PrayerTimes(calc_method, asr_method)
    times = pt.calc_times(date, timezone, long, lat)
    true_times = parse_line(line, date, timezone)

    output_correct(times, true_times)
    output_timezone_correct(times, timezone)


# TODO:
# 1. check locations where signs of longitude and timezone offset are different (ie. long = -170, timezone= +12)
# 2. check daylight savings time transition points
# 3. check high latitudes
