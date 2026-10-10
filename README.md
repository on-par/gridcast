# gridcast

gridcast answers a few simple questions about the Texas power grid: when was
load the highest, and which part of the state used the most? It reads a year of
hourly load data from ERCOT and prints small reports in your terminal.

## Why it exists

This is the demo repo for my PyTexas 2027 talk on On PAR Dev's Software Factory.
The factory picks up GitHub issues and turns them into reviewed, verified pull
requests, with a human approving the last step.

So the app is small and boring on purpose. The interesting part is the gates
around it. Every change has to pass the same four checks, whether a person or
an agent wrote it. The open issues are the work the factory will pick up on
stage.

Built by Patrick Robinson / [On PAR Dev](https://onpardev.com).

## Quickstart

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.13 for you if
you don't have it.

```bash
git clone https://github.com/on-par/gridcast.git
cd gridcast
uv sync
uv run gridcast --help
```

## What it does

Peak hour of each month, for the whole grid:

```text
$ uv run gridcast peak
Period      Peak hour              Load (MW)
2025-01     2025-01-22 HE08           77,478
2025-02     2025-02-20 HE08           80,525
2025-03     2025-03-25 HE18           62,920
2025-04     2025-04-14 HE18           65,614
2025-05     2025-05-23 HE17           78,392
2025-06     2025-06-19 HE17           77,351
2025-07     2025-07-30 HE18           81,707
2025-08     2025-08-18 HE18           83,679
2025-09     2025-09-04 HE18           79,918
2025-10     2025-10-02 HE17           75,889
2025-11     2025-11-17 HE16           64,698
2025-12     2025-12-15 HE08           63,131
```

`HE18` means "hour ending 18:00", so 5 to 6 PM. That's how ERCOT labels hours.
Use `--by day` for one row per day.

Weather zones ranked by total energy, busiest first:

```text
$ uv run gridcast zones
Zone        Energy (MWh)   Share
NCENT        134,085,972   27.5%
COAST        129,172,436   26.5%
SCENT         77,762,865   15.9%
FWEST         65,509,227   13.4%
SOUTH         38,848,324    8.0%
EAST          15,925,521    3.3%
NORTH         14,800,178    3.0%
WEST          12,129,056    2.5%

Busiest zone: NCENT
```

## How the code is laid out

```text
src/gridcast/
  models.py   frozen dataclasses: LoadReading, PeakHour, ZoneTotal
  load.py     reads the CSV with the standard library csv module
  reports.py  the reports, plain loops and dicts
  cli.py      the Typer command line
```

The logic uses only the standard library. No pandas, no numpy.

## The four gates

Run them all with `./verify.sh`. CI runs the same four on every pull request.

```bash
uv run ruff check           # lint
uv run ruff format --check  # formatting
uv run pyright              # type checking, strict mode
uv run pytest               # tests, including Hypothesis property tests,
                            # with 100% branch coverage required
```

## Data

`data/ercot_native_load_2025.csv` is ERCOT's hourly native load by weather zone
for 2025, from the
[Hourly Load Data Archives](https://www.ercot.com/gridinfo/load/load_hist).
Data courtesy of the Electric Reliability Council of Texas (ERCOT).

ERCOT's [Terms of Use](https://www.ercot.com/help/terms) allow raw public data
to be reproduced and redistributed in compilations and analyses. This project
isn't affiliated with or endorsed by ERCOT, and the numbers come with no
guarantee. See [data/README.md](data/README.md) for the download date, what
changed from the original file, and the full terms note.

## License

MIT. See [LICENSE](LICENSE). The ERCOT data is covered by ERCOT's terms, above.
