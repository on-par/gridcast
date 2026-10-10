"""Command line interface: `gridcast peak` and `gridcast zones`."""

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from gridcast.load import load_readings
from gridcast.reports import Period, busiest_zone, peak_hours, zone_totals

DEFAULT_DATA = Path("data/ercot_native_load_2025.csv")

app = typer.Typer(help="Reports over ERCOT hourly grid load data.", no_args_is_help=True)

DataOption = Annotated[
    Path,
    typer.Option("--data", help="ERCOT native load CSV file.", exists=True, dir_okay=False),
]


class GroupBy(StrEnum):
    DAY = "day"
    MONTH = "month"


def format_mw(value: float) -> str:
    """Format megawatts like '85,509'."""
    return f"{value:,.0f}"


@app.command()
def peak(
    data: DataOption = DEFAULT_DATA,
    by: Annotated[GroupBy, typer.Option("--by", help="Group by day or month.")] = GroupBy.MONTH,
) -> None:
    """Show the peak hour of each day or month."""
    period: Period = "day" if by is GroupBy.DAY else "month"
    typer.echo(f"{'Period':<12}{'Peak hour':<20}{'Load (MW)':>12}")
    for row in peak_hours(load_readings(data), period):
        when = f"{row.day.isoformat()} HE{row.hour_ending:02d}"
        typer.echo(f"{row.period:<12}{when:<20}{format_mw(row.total_mw):>12}")


@app.command()
def zones(data: DataOption = DEFAULT_DATA) -> None:
    """Rank weather zones by total energy used, busiest first."""
    readings = load_readings(data)
    top = busiest_zone(readings)
    if top is None:
        typer.echo("No readings found.")
        return
    ranked = zone_totals(readings)
    grand_total = sum(row.total_mwh for row in ranked)
    typer.echo(f"{'Zone':<8}{'Energy (MWh)':>16}{'Share':>8}")
    for row in ranked:
        share = row.total_mwh / grand_total
        typer.echo(f"{row.zone:<8}{format_mw(row.total_mwh):>16}{share:>8.1%}")
    typer.echo(f"\nBusiest zone: {top.zone}")
