from enum import Enum, auto, unique
import datetime as dt
import math

from .calculations import time_zenith, time_altitude, time_shadow_factor


@unique
class CalculationMethod(Enum):
    ISNA = auto()
    MWL = auto()
    EGYPT = auto()
    TEHRAN = auto()
    JAFARI = auto()
    MAKKAH = auto()
    KARACHI = auto()


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

        Asr calculation method is provided as an arugment, and Fajr is when Sun is at
        fajr_altitude_deg below the horizon. Isha is similarly when Sun is at isha_altitude_deg
        below the horizon. Sunrise is when the Sun is 0.833 degrees below the horizon (accounting
        for diameter and atmospheric refraction) and Maghrib is at sunset, which is at the same
        angle (0.833 degrees) except after noon. Dhuhr is when sun is at it's peak, and Asr is when
        the shadow of an object is either the same length as the height of the object, or twice that
        length, depending on the asr_method provided.

        Raises:
            ValueError: If asr_method is not of type AsrMethod


        Args:
            fajr_altitude_deg (float): Altitude of Sun for Fajr in degrees below horizon
            isha_altitude_deg (float): Altitude of Sun for Isha in degrees below horizon
            asr_method (AsrMethod, optional): Method to calculate Asr time. Defaults to
                AsrMethod.STANDARD.
        """
        self.asr_method = asr_method

        if self.asr_method == AsrMethod.STANDARD:
            self.shadow_factor = 1
        elif self.asr_method == AsrMethod.HANAFI:
            self.shadow_factor = 2
        else:
            raise ValueError(f"Unknown AsrMethod {self.asr_method}")

        self.fajr_altitude = -math.radians(fajr_altitude_deg)
        self.isha_altitude = -math.radians(isha_altitude_deg)
        self.sunset_altitude = -math.radians(0.833)

    def calc_times(
        self, date: dt.date, timezone: dt.tzinfo, longitude: float, latitude: float
    ) -> "dict[str, dt.datetime]":
        """Calculates prayer times.

        Args:
            date (dt.date): Date to calculate the prayer times for. This centers dhuhr on the date
                and the other prayer times are calculated surrounding it.
            timezone (dt.tzinfo): Timezone of the output datetimes
            longitude (float): Longitude of position in degrees East
            latitude (float): Latitude of position in degrees North

        Returns:
            dict[str, dt.datetime]: dictionary from time of interest (string) to time
        """
        # use zenith as reference point for other calculations.
        zenith = time_zenith(date, longitude)

        fajr = time_altitude(zenith, self.fajr_altitude, latitude, True)
        sunrise = time_altitude(zenith, self.sunset_altitude, latitude, True)
        asr = time_shadow_factor(zenith, self.shadow_factor, latitude, False)
        maghrib = time_altitude(zenith, self.sunset_altitude, latitude, False)
        isha = time_altitude(zenith, self.isha_altitude, latitude, False)

        times = {
            "fajr": fajr,
            "sunrise": sunrise,
            "dhuhr": zenith,
            "asr": asr,
            "maghrib": maghrib,
            "isha": isha,
        }

        for name in times:
            times[name] = times[name].astimezone(timezone)
        return times


class TehranMethod(GeneralMethod):
    """Uses Fajr angle 17.7 deg, Isha angle 14 deg, Maghrib angle 4.5"""

    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        super().__init__(17.7, 14, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.tzinfo, longitude: float, latitude: float):
        times = super().calc_times(date, timezone, longitude, latitude)

        # maghrib time is different
        zenith = time_zenith(date, longitude)
        magrib_altitude = -math.radians(4.5)
        times["maghrib"] = time_altitude(zenith, magrib_altitude, latitude, rising=False).astimezone(timezone)

        return times


class JafariMethod(GeneralMethod):
    """Uses Fajr angle 16 deg, Isha angle 14 deg, Maghrib angle 4 deg"""

    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        super().__init__(16, 14, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.tzinfo, longitude: float, latitude: float):
        times = super().calc_times(date, timezone, longitude, latitude)

        # maghrib time is different
        zenith = time_zenith(date, longitude)
        magrib_altitude = -math.radians(4)
        times["maghrib"] = time_altitude(zenith, magrib_altitude, latitude, rising=False).astimezone(timezone)

        return times


class MakkahMethod(GeneralMethod):
    """Uses Fajr angle 18.5 deg, Isha 90 minutes after Maghrib in general and
    120 during Ramadan.

    Note that Ramadan is calculated with additional dependency hijri-converter
    """

    def __init__(self, asr_method: AsrMethod = AsrMethod.STANDARD):
        try:
            import hijri_converter
        except ImportError:
            raise ImportError("Install hijri-converter to use MakkahMethod")

        # Isha angle not used, so use Fajr angle as substitute
        super().__init__(18.5, 18.5, asr_method=asr_method)

    def calc_times(self, date: dt.date, timezone: dt.tzinfo, longitude: float, latitude: float):
        from hijri_converter import Gregorian

        times = super().calc_times(date, timezone, longitude, latitude)

        hijri_date = Gregorian(date.year, date.month, date.day).to_hijri()
        if hijri_date.month == 9:
            times["isha"] = times["maghrib"] + dt.timedelta(minutes=120)
        else:
            times["isha"] = times["maghrib"] + dt.timedelta(minutes=90)

        return times


def PrayerTimes(method=CalculationMethod.MWL, asr=AsrMethod.STANDARD) -> GeneralMethod:
    """Generates an object that can be used to generate prayer times.

    Args:
        method (CalculationMethod): Method to use for general calculations.
            Defaults to CalculationMethod.MWL.
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
    elif method == CalculationMethod.KARACHI:
        return GeneralMethod(18, 18, asr)
    elif method == CalculationMethod.TEHRAN:
        return TehranMethod(asr)
    elif method == CalculationMethod.JAFARI:
        return JafariMethod(asr)
    elif method == CalculationMethod.MAKKAH:
        return MakkahMethod(asr)
    else:
        raise ValueError(f"Unknown CalculationMethod {method}")
