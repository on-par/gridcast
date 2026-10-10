"""Data types used across gridcast."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LoadReading:
    """One hour of load for one ERCOT weather zone.

    ERCOT labels hours by when they end, from 1 to 24. Hour ending 1 covers
    midnight to 1 AM, and hour ending 24 covers 11 PM to midnight. Both belong
    to the same operating day, so we keep the day and the hour separately.

    On the fall daylight saving change, hour ending 2 happens twice. The
    second one has repeated_hour set to True.
    """

    day: date
    hour_ending: int
    zone: str
    mw: float
    repeated_hour: bool = False


@dataclass(frozen=True)
class PeakHour:
    """The hour with the highest total load in a day or month."""

    period: str
    day: date
    hour_ending: int
    total_mw: float


@dataclass(frozen=True)
class ZoneTotal:
    """Total energy used by one weather zone, in megawatt-hours."""

    zone: str
    total_mwh: float
