"""Reports over load readings. Plain loops and dicts, no dataframes."""

from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from typing import Literal

from gridcast.models import LoadReading, PeakHour, ZoneTotal

Period = Literal["day", "month"]

# One hour of the system: operating day, hour ending, repeated DST hour.
HourKey = tuple[date, int, bool]


def system_totals(readings: Iterable[LoadReading]) -> dict[HourKey, float]:
    """Add up every zone for each hour to get the whole-grid load."""
    totals: dict[HourKey, float] = defaultdict(float)
    for reading in readings:
        totals[(reading.day, reading.hour_ending, reading.repeated_hour)] += reading.mw
    return dict(totals)


def period_label(day: date, period: Period) -> str:
    """Label a day as '2025-08-14' or '2025-08'."""
    if period == "day":
        return day.isoformat()
    return f"{day.year}-{day.month:02d}"


def peak_hours(readings: Iterable[LoadReading], period: Period = "day") -> list[PeakHour]:
    """Find the hour with the highest whole-grid load in each day or month.

    Ties go to the earlier hour. Results are in date order.
    """
    peaks: dict[str, PeakHour] = {}
    for (day, hour, _repeated), total in sorted(system_totals(readings).items()):
        label = period_label(day, period)
        current = peaks.get(label)
        if current is None or total > current.total_mw:
            peaks[label] = PeakHour(label, day, hour, total)
    return list(peaks.values())


def zone_totals(readings: Iterable[LoadReading]) -> list[ZoneTotal]:
    """Total energy per weather zone, busiest first.

    Each reading is one hour, so adding megawatts gives megawatt-hours.
    """
    totals: dict[str, float] = defaultdict(float)
    for reading in readings:
        totals[reading.zone] += reading.mw
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return [ZoneTotal(zone, total) for zone, total in ranked]


def busiest_zone(readings: Iterable[LoadReading]) -> ZoneTotal | None:
    """The weather zone that used the most energy, or None with no data."""
    ranked = zone_totals(readings)
    return ranked[0] if ranked else None
