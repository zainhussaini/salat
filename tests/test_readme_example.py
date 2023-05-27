import io
from contextlib import redirect_stdout


sample_code = """import salat
import datetime as dt
import pytz
import tabulate


# set up calculation methods
pt = salat.PrayerTimes(salat.CalculationMethod.ISNA, salat.AsrMethod.STANDARD)

# January 1, 2000
date = dt.date(2000, 1, 1)

# using NYC
longitude = -74.0060 # degrees East
latitude = 40.7128 # degrees North
eastern = pytz.timezone('US/Eastern')

# calculate times
prayer_times = pt.calc_times(date, eastern, longitude, latitude)

# print in a table
table = [["Name", "Time"]]
for name, time in prayer_times.items():
    readable_time = time.strftime("%m/%d/%Y, %I:%M:%S %p %Z")
    table.append([name, readable_time])
print(tabulate.tabulate(table, headers='firstrow'))
"""

expected = """Name     Time
-------  ---------------------------
fajr     01/01/2000, 05:58:15 AM EST
sunrise  01/01/2000, 07:20:09 AM EST
dhuhr    01/01/2000, 11:59:25 AM EST
asr      01/01/2000, 02:20:58 PM EST
maghrib  01/01/2000, 04:38:50 PM EST
isha     01/01/2000, 06:00:44 PM EST
"""

def test():
    f = io.StringIO()
    with redirect_stdout(f):
        exec(sample_code)
    out = f.getvalue()
    print(out)

    assert out[0:10] == expected[0:10]
