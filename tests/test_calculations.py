import datetime as dt
import math
from salat.calculations import *

EOT_MARGIN = 1 # seconds
KEPLER_SOLVE_MARGIN = 1e-3 # relative tolerance
ALTITUDE_MARGIN = 1e-5 # relative tolerance

def test_eot1():
    time = dt.datetime(2023, 1, 1, hour=12, tzinfo=dt.timezone.utc)
    # http://www.ppowers.com/EoT.htm
    eot_expected = dt.timedelta(minutes=-3, seconds=-27)

    eot, decl = eot_decl(time)
    assert math.isclose(eot.total_seconds(), eot_expected.total_seconds(), abs_tol=EOT_MARGIN)


def test_eot2():
    time = dt.datetime(2023, 5, 1, hour=12, tzinfo=dt.timezone.utc)
    # http://www.ppowers.com/EoT.htm
    eot_expected = dt.timedelta(minutes=2, seconds=52)

    eot, decl = eot_decl(time)
    assert math.isclose(eot.total_seconds(), eot_expected.total_seconds(), abs_tol=EOT_MARGIN)


def test_eot3():
    time = dt.datetime(2023, 9, 1, hour=12, tzinfo=dt.timezone.utc)
    # http://www.ppowers.com/EoT.htm
    eot_expected = dt.timedelta(seconds=-6)

    eot, decl = eot_decl(time)
    assert math.isclose(eot.total_seconds(), eot_expected.total_seconds(), abs_tol=EOT_MARGIN)


def test_kepler_solve():
    # http://www.jgiesen.de/kepler/kepler.html
    M = math.radians(27)
    e = 0.5
    E_expected = math.radians(48.43)
    E = kepler_solve(M, e)
    assert math.isclose(E, E_expected, rel_tol=KEPLER_SOLVE_MARGIN)


def test_calc_altitude1():
    latitude = 0
    declination = 0

    phi = math.radians(latitude)
    delta = declination
    zenith_alt = math.asin(math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta))
    assert math.isclose(zenith_alt, math.pi/2, rel_tol=ALTITUDE_MARGIN)

    shadow_factor = 1
    alt = calc_altitude(shadow_factor, declination, latitude)
    assert math.isclose(alt, math.pi/4, rel_tol=ALTITUDE_MARGIN)

    shadow_factor = 2
    alt = calc_altitude(shadow_factor, declination, latitude)
    assert math.isclose(alt, 0.463648, rel_tol=ALTITUDE_MARGIN)


def test_calc_altitude2():
    latitude = 20
    declination = math.radians(latitude)

    phi = math.radians(latitude)
    delta = declination
    zenith_alt = math.asin(math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta))
    assert math.isclose(zenith_alt, math.pi/2, rel_tol=ALTITUDE_MARGIN)

    shadow_factor = 1
    alt = calc_altitude(shadow_factor, declination, latitude)
    assert math.isclose(alt, math.pi/4, rel_tol=ALTITUDE_MARGIN)

    shadow_factor = 2
    alt = calc_altitude(shadow_factor, declination, latitude)
    assert math.isclose(alt, 0.463648, rel_tol=ALTITUDE_MARGIN)


def test_calc_altitude3():
    latitude = 20
    declination = 0

    phi = math.radians(latitude)
    delta = declination
    zenith_alt = math.asin(math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta))
    assert math.isclose(zenith_alt, math.pi/2 - math.radians(latitude), rel_tol=ALTITUDE_MARGIN)
    shadow_factor_zenith = abs(math.tan(phi - delta))

    shadow_factor = 1
    alt = calc_altitude(shadow_factor, declination, latitude)
    total_shadow_factor = 1/math.tan(alt)
    assert math.isclose(total_shadow_factor, shadow_factor_zenith + shadow_factor, rel_tol=ALTITUDE_MARGIN)

    shadow_factor = 2
    alt = calc_altitude(shadow_factor, declination, latitude)
    total_shadow_factor = 1/math.tan(alt)
    assert math.isclose(total_shadow_factor, shadow_factor_zenith + shadow_factor, rel_tol=ALTITUDE_MARGIN)


def test_calc_altitude4():
    latitude = -20
    declination = 0

    phi = math.radians(latitude)
    delta = declination
    zenith_alt = math.asin(math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta))
    assert math.isclose(zenith_alt, math.pi/2 - math.radians(abs(latitude)), rel_tol=ALTITUDE_MARGIN)
    shadow_factor_zenith = abs(math.tan(phi - delta))

    shadow_factor = 1
    alt = calc_altitude(shadow_factor, declination, latitude)
    total_shadow_factor = 1/math.tan(alt)
    assert math.isclose(total_shadow_factor, shadow_factor_zenith + shadow_factor, rel_tol=ALTITUDE_MARGIN)

    shadow_factor = 2
    alt = calc_altitude(shadow_factor, declination, latitude)
    total_shadow_factor = 1/math.tan(alt)
    assert math.isclose(total_shadow_factor, shadow_factor_zenith + shadow_factor, rel_tol=ALTITUDE_MARGIN)


def test_timedelta_at_altitude():
    # TODO: add test
    pass


def test_linear_interpolation():
    # TODO: add test
    pass


def test_time_zenith1():
    date = dt.date(2000, 1, 1)
    longitude = 0
    zenith = time_zenith(date, longitude)

    # check that equation is satisfied
    utc_noon = dt.datetime(date.year, date.month, date.day, 12, tzinfo=dt.timezone.utc)
    eot, _ = eot_decl(zenith)
    zenith_calc = utc_noon - dt.timedelta(hours=longitude/15) - eot

    assert math.isclose((zenith_calc - zenith).total_seconds(), 0)

    # check that it's on the right day
    assert -12 < (zenith - utc_noon).total_seconds()/60/60 < 12


def test_time_zenith2():
    date = dt.date(2000, 1, 1)
    longitude = 179
    zenith = time_zenith(date, longitude)

    # check that equation is satisfied
    utc_noon = dt.datetime(date.year, date.month, date.day, 12, tzinfo=dt.timezone.utc)
    eot, _ = eot_decl(zenith)
    zenith_calc = utc_noon - dt.timedelta(hours=longitude/15) - eot

    assert math.isclose((zenith_calc - zenith).total_seconds(), 0)

    # check that it's on the right day
    assert -12 < (zenith - utc_noon).total_seconds()/60/60 < 12


def test_time_zenith3():
    date = dt.date(2000, 1, 1)
    longitude = -179
    zenith = time_zenith(date, longitude)

    # check that equation is satisfied
    utc_noon = dt.datetime(date.year, date.month, date.day, 12, tzinfo=dt.timezone.utc)
    eot, _ = eot_decl(zenith)
    zenith_calc = utc_noon - dt.timedelta(hours=longitude/15) - eot

    assert math.isclose((zenith_calc - zenith).total_seconds(), 0)

    # check that it's on the right day
    assert -12 < (zenith - utc_noon).total_seconds()/60/60 < 12


def test_time_altitude1():
    date = dt.date(2000, 1, 1)
    latitude = 0
    longitude = 0

    altitude = math.pi/4

    zenith = time_zenith(date, longitude)

    time_alt = time_altitude(zenith, altitude, latitude, True)
    _, declination = eot_decl(time_alt)
    time_alt_calc = zenith - timedelta_at_altitude(altitude, declination, latitude)
    assert math.isclose((time_alt_calc - time_alt).total_seconds(), 0)

    time_alt = time_altitude(zenith, altitude, latitude, False)
    _, declination = eot_decl(time_alt)
    time_alt_calc = zenith + timedelta_at_altitude(altitude, declination, latitude)
    assert math.isclose((time_alt_calc - time_alt).total_seconds(), 0)


def test_time_altitude2():
    date = dt.date(2000, 1, 1)
    latitude = -60
    longitude = 150

    altitude = math.pi/6

    zenith = time_zenith(date, longitude)

    rising = True
    time_alt = time_altitude(zenith, altitude, latitude, rising)
    _, declination = eot_decl(time_alt)
    time_alt_calc = zenith - timedelta_at_altitude(altitude, declination, latitude)
    assert math.isclose((time_alt_calc - time_alt).total_seconds(), 0)

    rising = False
    time_alt = time_altitude(zenith, altitude, latitude, rising)
    _, declination = eot_decl(time_alt)
    time_alt_calc = zenith + timedelta_at_altitude(altitude, declination, latitude)
    assert math.isclose((time_alt_calc - time_alt).total_seconds(), 0)


def test_time_shadow_factor():
    date = dt.date(2000, 1, 1)
    latitude = -60
    longitude = 150

    zenith = time_zenith(date, longitude)

    shadow_factor = 1
    time_shadow = time_shadow_factor(zenith, shadow_factor, latitude, False)
    _, declination = eot_decl(time_shadow)
    altitude = calc_altitude(shadow_factor, declination, latitude)
    time_shadow_calc = zenith + timedelta_at_altitude(altitude, declination, latitude)
    assert math.isclose((time_shadow_calc - time_shadow).total_seconds(), 0)

    shadow_factor = 2
    time_shadow = time_shadow_factor(zenith, shadow_factor, latitude, False)
    _, declination = eot_decl(time_shadow)
    altitude = calc_altitude(shadow_factor, declination, latitude)
    time_shadow_calc = zenith + timedelta_at_altitude(altitude, declination, latitude)
    assert math.isclose((time_shadow_calc - time_shadow).total_seconds(), 0)
