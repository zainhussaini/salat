import salat
import pytz
from datetime import datetime

def test_ISNA():
    pt = salat.PrayerTimes(salat.CalculationMethod.ISNA, salat.AsrMethod.STANDARD)
    eastern = pytz.timezone('US/Eastern')
    # address of NYC
    longitude = -74.0060 # degrees East
    latitude = 40.7128 # degrees North

    prayer_times = pt.calc_times(datetime.now().date(), eastern, longitude, latitude)
    for name, prayer_time in prayer_times.items():
        print(name, prayer_time)