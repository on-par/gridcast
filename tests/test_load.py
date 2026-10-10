from datetime import date
from pathlib import Path

import pytest

from gridcast.load import load_readings, parse_hour_ending, parse_rows
from gridcast.models import LoadReading

SNAPSHOT = Path(__file__).parent.parent / "data" / "ercot_native_load_2025.csv"


def test_parse_hour_ending_regular_hour() -> None:
    assert parse_hour_ending("01/31/2025 23:00") == (date(2025, 1, 31), 23, False)


def test_hour_ending_24_stays_on_its_own_day() -> None:
    assert parse_hour_ending("01/31/2025 24:00") == (date(2025, 1, 31), 24, False)


def test_parse_hour_ending_repeated_dst_hour() -> None:
    assert parse_hour_ending("11/02/2025 02:00 DST") == (date(2025, 11, 2), 2, True)


@pytest.mark.parametrize("text", ["01/31/2025 00:00", "01/31/2025 25:00"])
def test_parse_hour_ending_rejects_out_of_range_hours(text: str) -> None:
    with pytest.raises(ValueError, match="between 1 and 24"):
        parse_hour_ending(text)


def test_parse_rows_makes_one_reading_per_zone_and_skips_total() -> None:
    rows = [{"hour_ending": "02/01/2025 01:00", "COAST": "90.5", "WEST": "40", "ERCOT": "130.5"}]
    assert parse_rows(rows) == [
        LoadReading(date(2025, 2, 1), 1, "COAST", 90.5),
        LoadReading(date(2025, 2, 1), 1, "WEST", 40.0),
    ]


def test_load_readings_from_sample_file(sample_csv: Path) -> None:
    readings = load_readings(sample_csv)
    assert len(readings) == 6 * 3
    assert readings[0] == LoadReading(date(2025, 1, 31), 23, "COAST", 100.0)
    assert sum(1 for r in readings if r.repeated_hour) == 3


def test_load_readings_empty_file(empty_csv: Path) -> None:
    assert load_readings(empty_csv) == []


def test_snapshot_has_one_full_year_for_eight_zones() -> None:
    readings = load_readings(SNAPSHOT)
    assert len(readings) == 8760 * 8
    assert {r.zone for r in readings} == {
        "COAST", "EAST", "FWEST", "NORTH", "NCENT", "SOUTH", "SCENT", "WEST"
    }  # fmt: skip
    assert min(r.day for r in readings) == date(2025, 1, 1)
    assert max(r.day for r in readings) == date(2025, 12, 31)
