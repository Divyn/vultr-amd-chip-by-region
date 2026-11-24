# Which Vultr region gives you the fast AMD chip?

The question: the same Vultr plan, High Performance AMD, does not always get the same CPU. Does the region you pick change which chip you get, and how fast the same code runs?

This follows up [intel-vs-amd-cloud-servers](https://github.com/Divyn/intel-vs-amd-cloud-servers), where 2 of 8 AMD servers in Seattle got the newer EPYC Genoa and ran the same jobs 1.63 times faster than the 6 that got EPYC Rome.

## Setup

- Host: Vultr. Plan: High Performance AMD (`vhp-2c-4gb-amd`), 2 vCPU, 4 GB RAM, $24 a month. Debian 13.
- 28 servers, all on that one plan:
  - 4 each in New Jersey (ewr), Frankfurt (fra), Mumbai (bom), Singapore (sgp) and Sydney (syd), run on 2026-11-24, every job started between 14:22 and 14:27 UTC
  - the 8 Seattle (sea) AMD servers from the first run, same rig, same day, 06:16 to 06:28 UTC
- Versions on every server: Python 3.13.5, pandas 3.1.1, numpy 2.5.5, gcc 14.2.0, zstd 1.5.7 (`results/versions.txt`).
- The CPU each server got is what `lscpu` printed on it (`results/per_server/*.hardware.txt`).

## The jobs

The same 5 jobs as the first run, on the same input files (made with a fixed seed, so every server reads the same bytes):

| Job | What it does | Cores |
| --- | --- | --- |
| `orderbook` | replays 1,000,000 orders through a pure Python order book, 3 times | 1 |
| `pandas_csv` | reads a 3,000,000 row trades CSV, adds a column, groups by symbol, sorts, writes | 1 |
| `json` | loads 500,000 orders from JSON, adds a field, dumps them back | 1 |
| `compile_sqlite` | `gcc -O2 -c sqlite3.c` (SQLite 3.54.1 amalgamation) | 1 |
| `zstd_2_cores` | `zstd -T2 -12` on the trades CSV | 2 |

3 rounds, the job order rotated each round. The score is seconds, the median of the 3 rounds; the total is the sum of the 5 medians. Lower is faster.

## Results by region

| Region | Servers | Chips they got | Fastest (s) | Slowest (s) | Median (s) |
| --- | --- | --- | --- | --- | --- |
| Frankfurt | 4 | Genoa 4 | 24.30 | 27.74 | 26.61 |
| Seattle | 8 | Genoa 2, Rome 6 | 25.65 | 43.13 | 41.17 |
| Sydney | 4 | Rome 4 | 37.88 | 39.90 | 38.33 |
| New Jersey | 4 | Milan 3, Rome 1 | 34.91 | 64.64 | 39.91 |
| Mumbai | 4 | Rome 4 | 45.84 | 51.00 | 50.64 |
| Singapore | 4 | Milan 2, Rome 2 | 36.43 | 70.87 | 59.17 |

Every server is in `results/summary_median_of_3.csv`, every single run in `results/all_runs.csv`, and the region table above in `results/by_region.csv`.

## Results by chip

| Chip | Servers | Fastest (s) | Slowest (s) | Median (s) |
| --- | --- | --- | --- | --- |
| AMD EPYC Genoa | 6 | 24.30 | 27.74 | 25.78 |
| AMD EPYC Milan | 5 | 34.91 | 48.44 | 38.64 |
| AMD EPYC Rome | 17 | 37.88 | 70.87 | 42.02 |

What it shows:

- All 4 Frankfurt servers got Genoa. All 4 in Mumbai and all 4 in Sydney got Rome. New Jersey and Singapore handed out a third chip, EPYC Milan, which the Seattle run never saw.
- Genoa only came up in Frankfurt and Seattle: 6 of 28 servers.
- The fastest server (Frankfurt, Genoa, 24.30 s) and the slowest (Singapore, Rome, 70.87 s) were on the same plan at the same price. The slowest took 2.92 times as long.
- The same chip was not the same speed everywhere. Rome servers ranged from 37.88 s (Sydney) to 70.87 s (Singapore).
- 4 regions per chip is a small sample. It shows what these servers got on this day, not the odds a region will give you.

## Steal time and reruns

Steal time (CPU time the host gave to other customers while a job ran, read from `/proc/stat`) was logged for every job; `max_steal_pct` in the summary is the highest on any job of that server.

- In Frankfurt, Seattle, Sydney and Mumbai it never went above 0.30%.
- 7 servers went above 1%, all in New Jersey or Singapore. The highest was `sgp-c` (Milan) at 20.18% on one job, so part of that server's time is busy neighbours, not the chip.
- The 3 slowest servers, all Rome, took nearly twice as long as the Sydney Rome servers, while their highest steal on any job was 0.16% (`ewr-a`), 1.80% (`sgp-a`) and 6.73% (`sgp-b`). Steal that size does not account for a gap that large; what does is not measured here. On `ewr-a` the first round was the slowest (the C compile took 55.07 s, then 49.23 s, then 40.59 s); the median is kept as measured.

Nothing was dropped or rerun. All 28 servers are in the tables.

## Run it yourself

On a fresh Debian 13 server, as root:

```
mkdir -p /root/exp && cp rig/* /root/exp/ && cd /root/exp
sh run.sh
cat STATUS results.csv hardware.txt
```

`run.sh` runs `setup.sh` (installs Python, pandas, gcc, zstd, downloads SQLite and checks its sha3-256, builds the input files), then `bench.sh` (the 5 jobs, 3 rounds). To see which chip you got, run:

```
lscpu | grep "Model name"
```
