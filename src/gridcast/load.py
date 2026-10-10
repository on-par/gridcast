"""Read ERCOT native load CSV files into LoadReading objects."""

import csv
from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path

from gridcast.models import LoadReading

HOUR_COLUMN = "hour_ending"
TOTAL_COLUMN = "ERCOT"
DST_SUFFIX = " DST"


def parse_hour_ending(text: str) -> tuple[date, int, bool]:
    """Turn '01/31/2025 24:00' into (date(2025, 1, 31), 24, False).

    A trailing ' DST' marks the repeated hour on the fall time change.
    """
    repeated = text.endswith(DST_SUFFIX)
    if repeated:
        text = text.removesuffix(DST_SUFFIX)
    day_text, time_text = text.split(" ")
    day = datetime.strptime(day_text, "%m/%d/%Y").date()
    hour = int(time_text.split(":")[0])
    if not 1 <= hour <= 24:
        raise ValueError(f"hour ending must be between 1 and 24, got {hour}")
    return day, hour, repeated


def parse_rows(rows: Iterable[dict[str, str]]) -> list[LoadReading]:
    """Turn wide CSV rows (one column per zone) into one reading per zone."""
    readings: list[LoadReading] = []
    for row in rows:
        day, hour, repeated = parse_hour_ending(row[HOUR_COLUMN])
        for column, value in row.items():
            if column in (HOUR_COLUMN, TOTAL_COLUMN):
                continue
            readings.append(LoadReading(day, hour, column, float(value), repeated))
    return readings


def load_readings(path: Path) -> list[LoadReading]:
    """Read every reading from an ERCOT native load CSV file."""
    with path.open(newline="") as file:
        return parse_rows(csv.DictReader(file))
