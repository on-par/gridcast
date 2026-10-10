from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from gridcast.models import LoadReading, PeakHour, ZoneTotal
from gridcast.reports import busiest_zone, peak_hours, period_label, system_totals, zone_totals

JAN_31 = date(2025, 1, 31)
FEB_1 = date(2025, 2, 1)


def reading(day: date, hour: int, zone: str, mw: float, repeated: bool = False) -> LoadReading:
    return LoadReading(day, hour, zone, mw, repeated)


SAMPLE = [
    reading(JAN_31, 23, "COAST", 100.0),
    reading(JAN_31, 23, "WEST", 50.0),
    reading(JAN_31, 24, "COAST", 150.0),
    reading(JAN_31, 24, "WEST", 50.0),
    reading(FEB_1, 1, "COAST", 90.0),
    reading(FEB_1, 1, "WEST", 40.0),
]


def test_system_totals_adds_zones_per_hour() -> None:
    assert system_totals(SAMPLE) == {
        (JAN_31, 23, False): 150.0,
        (JAN_31, 24, False): 200.0,
        (FEB_1, 1, False): 130.0,
    }


def test_period_label() -> None:
    assert period_label(date(2025, 8, 4), "day") == "2025-08-04"
    assert period_label(date(2025, 8, 4), "month") == "2025-08"


def test_peak_by_day_keeps_hour_ending_24_on_its_own_day() -> None:
    assert peak_hours(SAMPLE, "day") == [
        PeakHour("2025-01-31", JAN_31, 24, 200.0),
        PeakHour("2025-02-01", FEB_1, 1, 130.0),
    ]


def test_peak_by_month() -> None:
    assert peak_hours(SAMPLE, "month") == [
        PeakHour("2025-01", JAN_31, 24, 200.0),
        PeakHour("2025-02", FEB_1, 1, 130.0),
    ]


def test_peak_tie_goes_to_earlier_hour() -> None:
    tied = [reading(FEB_1, 5, "COAST", 10.0), reading(FEB_1, 3, "COAST", 10.0)]
    assert peak_hours(tied) == [PeakHour("2025-02-01", FEB_1, 3, 10.0)]


def test_repeated_dst_hour_is_its_own_hour() -> None:
    day = date(2025, 11, 2)
    readings = [reading(day, 2, "COAST", 80.0), reading(day, 2, "COAST", 85.0, repeated=True)]
    assert system_totals(readings) == {(day, 2, False): 80.0, (day, 2, True): 85.0}


def test_zone_totals_busiest_first_with_ties_by_name() -> None:
    readings = [*SAMPLE, reading(FEB_1, 2, "EAST", 340.0)]
    assert zone_totals(readings) == [
        ZoneTotal("COAST", 340.0),
        ZoneTotal("EAST", 340.0),
        ZoneTotal("WEST", 140.0),
    ]


def test_busiest_zone() -> None:
    assert busiest_zone(SAMPLE) == ZoneTotal("COAST", 340.0)


def test_busiest_zone_with_no_readings() -> None:
    assert busiest_zone([]) is None
    assert peak_hours([]) == []


# Property tests: random readings, rules that must always hold.

readings_strategy = st.lists(
    st.builds(
        LoadReading,
        day=st.dates(min_value=date(2025, 1, 1), max_value=date(2025, 3, 31)),
        hour_ending=st.integers(min_value=1, max_value=24),
        zone=st.sampled_from(["COAST", "NCENT", "WEST"]),
        mw=st.floats(min_value=0, max_value=30_000, allow_nan=False),
        repeated_hour=st.booleans(),
    ),
    max_size=60,
)


@given(readings_strategy)
def test_each_daily_peak_is_the_biggest_hour_of_that_day(readings: list[LoadReading]) -> None:
    totals = system_totals(readings)
    peaks = peak_hours(readings, "day")
    assert len(peaks) == len({day for day, _, _ in totals})
    for peak in peaks:
        same_day = [total for (day, _, _), total in totals.items() if day == peak.day]
        assert peak.total_mw == max(same_day)


@given(readings_strategy)
def test_zone_totals_are_sorted_and_cover_every_zone(readings: list[LoadReading]) -> None:
    ranked = zone_totals(readings)
    assert {row.zone for row in ranked} == {r.zone for r in readings}
    amounts = [row.total_mwh for row in ranked]
    assert amounts == sorted(amounts, reverse=True)
