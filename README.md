# salat

One of the pillars of Islam is salat, which is the act of praying five times a day. Each prayer has a specific time interval, defined in terms of the Sun's position, so anyone anywhere in the world can know when it is time to pray.

However with modern computation most Muslims use calculated prayer times to determine when to pray instead of watching the Sun. This package performs accurate calculations using orbital dynamics equations instead of common approximations, and native Python tools like datetime to calculate these times.

## Prayer Times

In general terms, the time range of a prayer is from it's start until the start of the next prayer, except for Fajr which ends at sunrise. The start of the prayer time intervals are the following:

| Name | Start of Time Range |
|------|------------|
| Fajr | Beginning of twilight |
| Sunrise | Sunrise. This marks the end of Fajr and is not its own prayer |
| Dhuhr | When the Sun passes its zenith |
| Asr | When the length of a shadow is the same as the length of the object (or with Hanafi method, twice the length of the object) plus its length when the Sun is at zenith |
| Maghrib | Sunset |
| Isha | When the red light of sunset is gone |

However there are various methods and standards for what exact times these general terms correspond to. For example, according to the Muslim World League, Fajr starts when the altitude of the Sun is 18 degrees below the horizon, while the Islamic Society of North America says 15 degrees below the horizon.

## Motivation

There are many websites with prayer time tables and apps that show automatically updating prayer times for your location for each day. However there are not many Python ones, and they either query the websites for time tables or use approximate methods.

This package has the following goals:
1. Accurate calculations using exact equations and high precision parameters where possible
2. Use developer friendly interface including datetimes and typehints
3. Support several calculation methods

## Supported methods
This package supports the following calculation methods:
1. ISNA (Islamic Society of North America)
2. MWL (Muslim World League)
3. EGYPT (Egyptian General Authority of Survey)
4. TEHRAN (Institute of Geophysics, University of Tehran)
5. JAFARI (Shia Ithna Ashari, Leva Research Institute, Qum)
6. MAKKAH (Umm al-Qura)
7. KARACHI (University Of Islamic Sciences, Karachi)

There are many more methods in use around the world, so if there's any missing that you would like to see please submit an issue.

## Installation
```shell
pip install salat
```

## Example code

```python
import salat
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
```

Output
```
Name     Time
-------  ---------------------------
fajr     01/01/2000, 05:58:15 AM EST
sunrise  01/01/2000, 07:20:09 AM EST
dhuhr    01/01/2000, 11:59:25 AM EST
asr      01/01/2000, 02:20:58 PM EST
maghrib  01/01/2000, 04:38:50 PM EST
isha     01/01/2000, 06:00:44 PM EST
```

## Planned features
1. Adjustment for higher altitudes
2. Options for Isha/Fajr calculation in high altitudes based on "middle of the night" and "sevent of the night" methods
3. Add additional calculation methods
