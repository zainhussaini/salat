import salat
import datetime as dt
from salat.methods import CalculationMethod, AsrMethod
from hypothesis import assume, given, settings, strategies as st


@settings(deadline=10, max_examples=10000)
@given(
    calc_method=st.sampled_from(CalculationMethod),
    asr_method=st.sampled_from(AsrMethod),
    date=st.dates(
        min_value=dt.date(1900, 1, 1), 
        max_value=dt.date(2100, 12, 31)
    ),
    timezone=st.timezones(),
    longitude=st.floats(min_value=-180.0, max_value=180.0),
    latitude=st.floats(min_value=-90.0, max_value=90.0)
)
def test_prayer_times_execution(calc_method, asr_method, date, timezone, longitude, latitude):
    """
    Tests that salat.calc_times executes without raising exceptions 
    for a wide range of valid geographical and temporal inputs.
    """
    # The hijri_converter package only supports dates 1 August 1924 CE to 16 November 2077 CE.
    if calc_method == CalculationMethod.MAKKAH:
        assume(dt.date(1924, 8, 1) <= date <= dt.date(2077, 11, 16))

    try:
        pt = salat.PrayerTimes(calc_method, asr_method)
        times = pt.calc_times(date, timezone, longitude, latitude)
        
        assert isinstance(times, dict)
        assert len(times) > 0
    except ValueError as error:
        # For certain altitudes and dates, the sun doesn't ever cross the horizon.
        if str(error) == "Sun does not reach altitude":
            return
        raise