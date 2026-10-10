# Data

`ercot_native_load_2025.csv` is a frozen snapshot of ERCOT's hourly native load
by weather zone for calendar year 2025. gridcast reads this file and never goes
to the network.

## Source

- Publisher: Electric Reliability Council of Texas (ERCOT)
- Page: Hourly Load Data Archives, https://www.ercot.com/gridinfo/load/load_hist
- File: Native Load 2025, https://www.ercot.com/files/docs/2025/02/11/Native_Load_2025.zip
- Downloaded: 2026-10-10

## What changed from the original

The ZIP holds one Excel sheet. We saved it as CSV and renamed the first column
from `Hour Ending` to `hour_ending`. The values are as published: 8,760 rows,
one per hour, with a column per weather zone (COAST, EAST, FWEST, NORTH, NCENT,
SOUTH, SCENT, WEST) plus the `ERCOT` system total. About 1.1 MB.

Two things to know about the times:

- ERCOT labels each hour by when it ends. `01/31/2025 24:00` is the last hour of
  January 31, not the first hour of February 1.
- On the fall daylight saving change, hour ending 2 happens twice. The second
  one is written as `11/02/2025 02:00 DST`.

## Terms

ERCOT's [Terms of Use](https://www.ercot.com/help/terms) (last updated
2023-07-20, section 5) say public website content "may be used, reproduced,
and redistributed" as long as it isn't modified and notices are kept, and that
"raw data provided in public portions of this website may be used, reproduced,
and redistributed in compilations, charts, and analyses without maintaining
such notices." This file is that raw public data, so we redistribute it here
with credit to ERCOT.

ERCOT doesn't guarantee the accuracy of compilations or analyses built from its
data, and neither does this project. "ERCOT" is a trademark of ERCOT. This
project isn't affiliated with or endorsed by ERCOT.
