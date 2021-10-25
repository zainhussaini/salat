import datetime as dt
from typing import Callable
import math


def eot_decl(time: dt.datetime) -> "tuple[dt.timedelta, float]":
    """Calculates the equation of time and Sun's declination at a given time.

    The term equation of time referes to the difference between mean solar time
    (what you would get if the sun had uniform motion along the celestial
    equator) and apparent solar time (what you would get by measuing the angle
    of the sun and calculating the time). This is because the ecliptic is tilted
    relative to Earth's equator and the Earth's orbit has eccentricity. See
    https://en.wikipedia.org/wiki/Equation_of_time

    The declination of the sun is the angle between the Sun's rays and the plane
    of Earth's equator. It's periodic with the orbit of Earth around the Sun.
    See https://en.wikipedia.org/wiki/Position_of_the_Sun

    Args:
        time (datetime): time to calculate equation of time and declination for

    Returns:
        float: equation of time (in minutes)
        float: declination of sun (in radians)
    """
    # January 1, 2000 at noon in UTC
    utc = dt.timezone(dt.timedelta())
    epoch = dt.datetime(2000, 1, 1, 12, tzinfo=utc)
    days_since_epoch = (time - epoch).total_seconds() / 60 / 60 / 24

    # e = 0.016709
    # lam_p = 4.938201
    # epsilon = 0.409093

    # account for secular effets, for unecessary level of accuracy
    y100 = days_since_epoch / 36525  # centuries since epoch
    e = 1.6709e-2 - 4.193e-5 * y100 - 1.26e-7 * y100 ** 2
    lam_p = math.radians(282.93807 + 1.7195 * y100 + 3.025e-4 * y100 ** 2)
    epsilon = math.radians(23.4393 - 0.013 * y100 -
                           2e-7 * y100 ** 2 + 5e-7 * y100 ** 3)

    MD = 6.24004077  # M at epoch (Jan 1 2000 at noon)
    TY = 365.2596358  # days in a year
    D = days_since_epoch % TY
    M = MD + 2 * math.pi * D / TY
    M = M % (2 * math.pi)
    E = KeplerSolve(M, e)

    nu = math.acos((math.cos(E) - e) / (1 - e * math.cos(E)))
    if E > math.pi:
        nu = 2 * math.pi - nu

    lam = nu + lam_p
    # put lam in range [0, 2*pi)
    lam = lam % (2 * math.pi)

    # if tan(lam) is infinity, alpha = lam, otherwise use atan equation and
    # match quadrant
    if math.isclose(math.cos(lam), 0):
        alpha = lam
    else:
        alpha = math.atan(math.cos(epsilon) * math.tan(lam))
        if lam < math.pi / 2:
            assert 0 <= alpha < math.pi / 2
        elif lam < math.pi * 3 / 2:
            alpha += math.pi
            assert math.pi / 2 <= alpha < math.pi * 3 / 2
        else:
            alpha += 2 * math.pi
            assert math.pi * 3 / 2 <= alpha < 2 * math.pi

    eot_rad = M + lam_p - alpha
    if eot_rad > math.pi:
        eot_rad -= 2 * math.pi

    eot_min = eot_rad / (2 * math.pi) * 60 * 24
    eot = dt.timedelta(minutes=eot_min)
    decl = math.asin(math.sin(epsilon) * math.sin(lam))

    return eot, decl


def KeplerSolve(M: float, e: float) -> float:
    """Solves Kepler's equation inverse problem for elliptical orbits.

    Args:
        M (float): mean anomaly
        e (float): eccentricity

    Returns:
        float: eccentric anomaly
    """
    if not 0 < e < 1:
        raise ValueError(
            "Eccentricity of elliptical orbit required in range (0, 1)")

    # find E such that M = E - e*sin(E)
    E = M
    while not math.isclose(M, E - e * math.sin(E)):
        E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        # E = M + e * math.sin(E)
    return E


def timedelta_at_altitude(
    altitude: float, declination: float, latitude: float
) -> dt.timedelta:
    """Calculates the difference from Dhuhr to the time when Sun is at altitude.

    Args:
        altitude (float): Altitude of sun in radians
        declination (float): Declination of sun in radians
        latitude (float): Latitude of position on Earth in degrees North

    Returns:
        timedelta: Offset from Dhuhr. Note that this is always positive
    """
    alpha = altitude
    phi = math.radians(latitude)
    delta = declination
    numerator = -math.sin(alpha) - math.sin(phi) * math.sin(delta)
    denominator = math.cos(phi) * math.cos(delta)
    cos_hour_rad = numerator / denominator
    if cos_hour_rad < -1 or cos_hour_rad > 1:
        raise ValueError("Sun does not reach altitude")
    hour_rad = math.acos(cos_hour_rad)
    hours = hour_rad / (2 * math.pi) * 24
    return dt.timedelta(hours=hours)


def calc_dhuhr(date: dt.date, timezone: dt.tzinfo, longitude: float) -> dt.datetime:
    """Calculates time of Dhuhr on date at longitude, in the timezone given.

    Args:
        date (date): The date to calculate Dhuhr time for
        timezone (tzinfo): The timezone of the given date and the output
        longitude (float): The longitude in degrees East

    Returns:
        datetime: The specific time of Dhuhr on the date, with correct timezone
    """
    # this accounts for time zone (daylight savings included) and longitude
    utc = dt.timezone(dt.timedelta())
    utc_noon = dt.datetime(date.year, date.month, date.day, 12, tzinfo=utc)

    # the equation of time depends on the date (and therefore changes slightly
    # over the day) the time of dhuhr depends on the equation of time. therefore
    # this is a circular dependency, so use interpolation method to find
    # solution

    # x is the datetime guess
    # f(x) is the difference between time calculated using the guess's
    #   declination and the guess itself
    # here x is guess and f(x) is diff (found with calc_difference)

    def calc_difference(guess: dt.datetime) -> dt.timedelta:
        """Using guess to calculate eot, calculate the time of dhuhr, and return
        difference between guess and calculated dhuhr.
        """
        eot, declination = eot_decl(guess)
        actual = utc_noon - eot - dt.timedelta(hours=longitude / 15)
        return actual - guess

    # guess is when sun would be at zenith ignoring eot
    guess = utc_noon - dt.timedelta(hours=longitude/15)
    # eot is usually between -14 to +16 minutes, so bound that by guess1 and guess2
    guess1 = guess - dt.timedelta(minutes=20)
    guess2 = guess + dt.timedelta(minutes=20)

    return linear_interpolation(calc_difference, guess1, guess2)


def time_alt_first(
    date: dt.date,
    timezone: dt.tzinfo,
    altitude: float,
    longitude: float,
    latitude: float,
) -> dt.datetime:
    """Calculates the first time on the given date when the altitude of the sun
    is as given.

    Args:
        date (date): The date to calculate the time for
        timezone (tzinfo): The timezone of the given date and the output
        altitude (float): The desired altitude of the Sun BELOW THE HORIZON at
            the output time in radians
        longitude (float): The longitude in degrees East
        latitude (float): The latitude in degrees North

    Returns:
        datetime: The time on the given date when Sun's altitude is as given and
            the Sun is rising
    """
    dhuhr = calc_dhuhr(date, timezone, longitude)

    # the declination depends on the date (and therefore changes slightly over
    # the day) the time when the sun is at a given altitude depends on the
    # declination therefore this is a circular dependency, so use interpolation
    # method to find solution

    # x is the datetime guess
    # f(x) is the difference between time calculated using the guess's
    #   declination and the guess itself
    # here x is guess and f(x) is diff (found with calc_difference)

    def calc_difference(guess: dt.datetime) -> dt.timedelta:
        """Using guess to calculate declination, calculate the time of when Sun
        is at altitude, and return difference between guess and calculated time.
        """
        eot, declination = eot_decl(guess)
        T = timedelta_at_altitude(altitude, declination, latitude)
        actual = dhuhr - T
        return actual - guess

    # start guesses at midnight local time and dhuhr
    utc = dt.timezone(dt.timedelta())
    utc_midnight = dt.datetime(date.year, date.month, date.day, 0, tzinfo=utc)
    guess1 = utc_midnight - dt.timedelta(hours=longitude/15)
    guess2 = dhuhr

    return linear_interpolation(calc_difference, guess1, guess2)


def time_sf_first(
    date: dt.date,
    timezone: dt.tzinfo,
    shadow_factor: float,
    longitude: float,
    latitude: float,
) -> dt.datetime:
    """Calculates the first time in the day when shadow of an object is
    shadow_factor times its height.

    Args:
        date (date): The date to calculate Dhuhr time for
        timezone (tzinfo): The timezone of the given date and the output
        shadow_factor (float): Multiplication factor from height to shadow length
        longitude (float): The longitude in degrees East
        latitude (float): The latitude in degrees North

    Returns:
        datetime: The time immediately before dhuhr when shadow length is as given
    """
    dhuhr = calc_dhuhr(date, timezone, longitude)

    # the declination depends on the date (and therefore changes slightly over the day)
    # the time when the sun is at a given altitude depends on the declination
    # therefore this is a circular dependency, so use interpolation method to find solution

    # x is the datetime guess
    # f(x) is the difference between time calculated using the guess's
    #   declination and the guess itself
    # here x is guess and f(x) is diff (found with calc_difference)

    def calc_difference(guess: dt.datetime) -> dt.timedelta:
        """Using guess to calculate declination, calculate the time of when
        shadow is at given length, and return difference between guess and
        calculated time.
        """
        eot, declination = eot_decl(guess)
        altitude = calc_altitude(shadow_factor, declination, latitude)
        # negative altitude since timedelta_at_altitude uses altitude positive for below the horizon
        T = timedelta_at_altitude(-altitude, declination, latitude)
        actual = dhuhr - T
        return actual - guess

    # start guesses at midnight local time and dhuhr
    utc = dt.timezone(dt.timedelta())
    utc_midnight = dt.datetime(date.year, date.month, date.day, 0, tzinfo=utc)
    guess1 = utc_midnight - dt.timedelta(hours=longitude/15)
    guess2 = dhuhr

    return linear_interpolation(calc_difference, guess1, guess2)


def linear_interpolation(
    diff_function: Callable[[dt.datetime], dt.timedelta],
    guess1: dt.datetime,
    guess2: dt.datetime,
):
    """Uses linear interpolation to calculate when diff_function ouputs zero.

    More specifically, this uses the secant method to calculate guess such that
    diff_function(guess) is zero. For more information about the secant method
    see https://en.wikipedia.org/wiki/Secant_method

    Args:
        diff_function (Callable[[datetime, datetime], timedelta]): The
            function to find the root for
        guess1 (datetime): First guess
        guess2 (datetime): Second guess (cannot be the same as first guess)

    Returns:
        datetime: input to diff_function which results in zero timedelta output
    """
    if math.isclose((guess1 - guess2).total_seconds(), 0):
        raise ValueError("guess1 and guess2 need to be different")

    # make guess1 left of guess2
    if guess2 < guess1:
        guess1, guess2 = guess2, guess1

    diff1 = diff_function(guess1)
    diff2 = diff_function(guess2)
    # stop iteration when both guesses converge
    while not math.isclose((guess1 - guess2).total_seconds(), 0):
        guess3 = guess1 - diff1 * ((guess2 - guess1) / (diff2 - diff1))
        diff3 = diff_function(guess3)

        guess1, diff1 = guess2, diff2
        guess2, diff2 = guess3, diff3
    return guess1


def calc_altitude(shadow_factor: float, declination: float, latitude: float) -> float:
    """Calculates altitude when shadow of object is show_factor times the height
    of the object.

    Args:
        shadow_factor (float): Multiplication factor from height to shadow length
        declination (float): Declination of sun in radians
        latitude (float): The latitude in degrees North

    Returns:
        float: The Sun's altitude in radians
    """
    phi = math.radians(latitude)
    delta = declination
    alt = math.atan2(1, shadow_factor + math.tan(phi - delta))
    return alt
