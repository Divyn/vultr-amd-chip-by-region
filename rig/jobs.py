"""Time 5 everyday jobs, 3 rounds, rotating order. Prints one CSV line per job per round.

Columns: round,job,seconds,steal_pct
steal_pct is CPU time the host gave to other tenants while the job ran (from /proc/stat).
"""
import subprocess
import sys
import time

PY = "/root/v/bin/python"
JOBS = {
    "orderbook": "python3 orderbook.py ops.bin 3",
    "pandas_csv": f"{PY} pandas_job.py",
    "json": f"{PY} json_job.py",
    "compile_sqlite": "gcc -O2 -c sqlite3.c -o /tmp/sqlite3.o",
    "zstd_2_cores": "zstd -q -f -T2 -12 trades.csv -o /tmp/trades.csv.zst",
}
ROUNDS = 3


def cpu():
    parts = open("/proc/stat").readline().split()[1:]
    vals = list(map(int, parts))
    return sum(vals), vals[7]


def main():
    names = list(JOBS)
    print("round,job,seconds,steal_pct,started_utc", flush=True)
    for r in range(ROUNDS):
        order = names[r % len(names):] + names[:r % len(names)]
        for name in order:
            total0, steal0 = cpu()
            stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            t0 = time.perf_counter()
            res = subprocess.run(JOBS[name], shell=True, capture_output=True, text=True)
            secs = time.perf_counter() - t0
            total1, steal1 = cpu()
            if res.returncode != 0:
                print("FAILED", name, res.stderr[-400:], file=sys.stderr, flush=True)
                sys.exit(1)
            steal = 100.0 * (steal1 - steal0) / max(1, total1 - total0)
            print(f"{r + 1},{name},{secs:.3f},{steal:.2f},{stamp}", flush=True)


if __name__ == "__main__":
    main()
