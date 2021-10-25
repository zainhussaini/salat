from enum import Enum, auto, unique
import datetime as dt
import math

from .calculations import time_alt_first, time_sf_first, calc_dhuhr


@unique
class CalculationMethod(Enum):
    ISNA = auto()
    MWL = auto()
    EGYPT = auto()
    TEHRAN = auto()
    JAFARI = auto()


@unique
class AsrMethod(Enum):
    STANDARD = auto()
    HANAFI = auto()


class GeneralMethod:
    def __init__(
        self,
        fajr_altitude_deg: float,
        isha_altitude_deg: float,
        asr_method: AsrMethod = AsrMethod.STANDARD,
    ):
        """General system to define a method using Fajr and Isha altitudes.

        Asr calculation method is provided as an arugment, and Fajr is when Sun
        is at fajr_altitude_deg below the horizon. Isha is similarly when Sun is
        at isha_altitude_deg below the horizon. Midnight is halfway between
        sunset and sunrise. Sunrise is when the Sun is 0.833 degrees below the
        horizon (accounting for diameter and atmospheric refraction) and Maghrib
        is at sunset, which is at the same angle (0.833 degrees) except after
        noon. Dhuhr is when sun is at it's peak, and Asr is when the shadow of
        an object is either the same length as the height of the object, or
        twice that length, depending on the asr_method provided.

        Raises:
            ValueError: If asr_method is not of type AsrMethod


        Args:
            fajr_altitude_deg (float): Altitude of Sun for Fajr in degrees below horizon
            isha_altitude_deg (float): Altitude of Sun for Isha in degrees below horizon
            asr_method (AsrMethod, optional): Method to calculate Asr time.
                Defaults to AsrMethod.STANDARD.
        """
        self.asr_method = asr_method

        if self.asr_method == AsrMethod.STANDARD:
            self.shadow_factor = 1
        elif self.asr_method == AsrMethod.HANAFI:
            self.shadow_factor = 2
        else:
            raise ValueError(f"Unknown AsrMethod {self.asr_method}")

        self.fajr_altitude = math.radians(fajr_altitude_deg)
        self.isha_altitude = math.radians(isha_altitude_deg)

    def calc_times(
        self, date: dt.date, timezone: dt.timezone, longitude: float, latitude: float
    ) -> "dict[str, dt.datetime]":
        """Calculates prayer times including sunrise and midnight.

        Args:
            date (dt.date): Date to calculate the prayer times for. Note that
                "midnight" might be past 12 am therefore on next day
            timezone (dt.timezone): Timezone of the output datetimes
            longitude (float): Longitude of position in degrees East
            latitude (float): Latitude of position in degrees North

        Returns:
            dict[str, dt.datetime]: dictionary from time of interest (string) to time
        """
        sunset_altitude = math.radians(0.833)

        fajr = time_alt_first(date, timezone, self.fajr_altitude, longitude, latitude)

        sunrise = time_alt_first(date, timezone, sunset_altitude, longitude, latitude)

        dhuhr = calc_dhuhr(date, timezone, longitude)

        first = time_sf_first(date, timezone, self.shadow_factor, longitude, latitude)
        asr = dhuhr + (dhuhr - first)

        first = time_alt_first(date, timezone, sunset_altitude, longitude, latitude)
        maghrib = dhuhr + (dhuhr - first)

        first = time_alt_first(date, timezone, self.isha_altitude, longitude, latitude)
        isha = dhuhr + (dhuhr - first)

        next_date = date + dt.timedelta(days=1)
        next_sunrise = time_alt_first(next_date, timezone, sunset_altitude, longitude, latitude)
        midnight = maghrib + (next_sunrise - maghrib) / 2

        times = {
            "fajr": fajr,
            "sunrise": sunrise,
            "dhuhr": dhuhr,
            "asr": asr,
            "maghrib": maghrib,
            "isha": isha,
            "midnight": midnight,
        }
        return times


class TehranMethod(GeneralMethod):
    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        super().__init__(17.7, 14, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.timezone, longitude: float, latitude: float):
        magrib_altitude = math.radians(4.5)

        general_times = super().calc_times(date, timezone, longitude, latitude)
        sunset = general_times["maghrib"]

        # maghrib time is different, fajr time stays the same
        first = time_alt_first(date, timezone, magrib_altitude, longitude, latitude)
        dhuhr = general_times["dhuhr"]
        maghrib = dhuhr + (dhuhr - first)
        general_times["maghrib"] = maghrib

        # midnight is different, it is between sunset and fajr
        next_date = date + dt.timedelta(days=1)
        next_fajr = time_alt_first(next_date, timezone, self.fajr_altitude, longitude, latitude)
        midnight = sunset + (next_fajr - sunset) / 2
        general_times["midnight"] = midnight

        return general_times


class JafariMethod(GeneralMethod):
    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        super().__init__(16, 14, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.timezone, longitude: float, latitude: float):
        magrib_altitude = math.radians(4)

        general_times = super().calc_times(date, timezone, longitude, latitude)
        sunset = general_times["maghrib"]

        # maghrib time is different, fajr time stays the same
        first = time_alt_first(date, timezone, magrib_altitude, longitude, latitude)
        dhuhr = general_times["dhuhr"]
        maghrib = dhuhr + (dhuhr - first)
        general_times["maghrib"] = maghrib

        # midnight is different, it is between sunset and fajr
        next_date = date + dt.timedelta(days=1)
        next_fajr = time_alt_first(next_date, timezone, self.fajr_altitude, longitude, latitude)
        midnight = sunset + (next_fajr - sunset) / 2
        general_times["midnight"] = midnight

        return general_times


def PrayerTimes(method=CalculationMethod.MWL, asr=AsrMethod.STANDARD) -> GeneralMethod:
    """Generates an object that can be used to generate prayer times.

    Args:
        method (CalculationMethod): Method to use for general calculations.
            Defaults to CalculationMethod.ISNA.
        asr (AsrMethod): Method to determine Asr time. Defaults to
            AsrMethod.STANDARD.

    Raises:
        ValueError: If asr_method is not of type AsrMethod

    Returns:
        GeneralMethod: Class that you can use to calculate prayer times
    """
    if method == CalculationMethod.ISNA:
        return GeneralMethod(15, 15, asr)
    elif method == CalculationMethod.MWL:
        return GeneralMethod(18, 17, asr)
    elif method == CalculationMethod.EGYPT:
        return GeneralMethod(19.5, 17.5, asr)
    elif method == CalculationMethod.TEHRAN:
        return TehranMethod(asr)
    elif method == CalculationMethod.JAFARI:
        return JafariMethod(asr)
    else:
        raise ValueError(f"Unknown CalculationMethod {method}")
