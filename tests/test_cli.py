from pathlib import Path

from typer.testing import CliRunner

from gridcast.cli import app, format_mw

runner = CliRunner()


def test_format_mw() -> None:
    assert format_mw(85509.4) == "85,509"


def test_peak_by_month(sample_csv: Path) -> None:
    result = runner.invoke(app, ["peak", "--data", str(sample_csv)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines[0].split() == ["Period", "Peak", "hour", "Load", "(MW)"]
    assert lines[1].split() == ["2025-01", "2025-01-31", "HE24", "450"]
    assert lines[2].split() == ["2025-02", "2025-02-01", "HE01", "310"]
    assert lines[3].split() == ["2025-11", "2025-11-02", "HE02", "285"]


def test_peak_by_day(sample_csv: Path) -> None:
    result = runner.invoke(app, ["peak", "--data", str(sample_csv), "--by", "day"])
    assert result.exit_code == 0
    assert "2025-01-31  2025-01-31 HE24" in result.output


def test_peak_rejects_unknown_grouping(sample_csv: Path) -> None:
    result = runner.invoke(app, ["peak", "--data", str(sample_csv), "--by", "week"])
    assert result.exit_code != 0


def test_zones(sample_csv: Path) -> None:
    result = runner.invoke(app, ["zones", "--data", str(sample_csv)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines[1].split() == ["NCENT", "1,110", "58.0%"]
    assert lines[-1] == "Busiest zone: NCENT"


def test_zones_with_no_readings(empty_csv: Path) -> None:
    result = runner.invoke(app, ["zones", "--data", str(empty_csv)])
    assert result.exit_code == 0
    assert result.output.strip() == "No readings found."


def test_missing_data_file_is_an_error(tmp_path: Path) -> None:
    result = runner.invoke(app, ["zones", "--data", str(tmp_path / "nope.csv")])
    assert result.exit_code != 0
