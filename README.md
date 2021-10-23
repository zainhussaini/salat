# salat

## Motivation

There are a few other prayer time calculators, but not many Python ones, and of the ones for Python, they are all outdated and none use Python features such as datetime and type hints.

This package aims to be a very accurate calculation method for salat times, including sunrise and midnight.

## Supported methods
This package supports the following calculation methods:
1. ISNA (Islamic Society of North America)
2. MWL (Muslim World League)
3. Egypt (Egyptian General Authority of Survey)
4. Tehran (Institute of Geophysics, University of Tehran)
5. Jafari (Shia Ithna Ashari, Leva Research Institute, Qum)

There are many more methods in use around the world, so if there's any missing that you would like to see please submit an issue.

## Example code

```python
import salat
import pytz
from datetime import datetime

pt = salat.PrayerTimes(salat.CalculationMethod.ISNA, salat.AsrMethod.STANDARD)
eastern = pytz.timezone('US/Eastern')
# address of NYC
longitude = -74.0060 # degrees East
latitude = 40.7128 # degrees North

prayer_times = pt.calc_times(datetime.now().date(), eastern, longitude, latitude)
for name, prayer_time in prayer_times.items():
    print(name, prayer_time)
```

## Planned features
1. Adjustment for higher altitudes
2. Options for Isha/Fajr calculation in high altitudes based on "middle of the night" and "sevent of the night" methods
3. Add additional calculation methods like Makkah method by Umm al-Qura University, Makkah
