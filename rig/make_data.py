"""Make the input files every job reads. Same seed on every server, so every server gets the same bytes."""
import json
import random

random.seed(42)
SYMBOLS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "WIPRO"]

with open("trades.csv", "w") as f:
    f.write("time,symbol,price,qty\n")
    for i in range(3_000_000):
        f.write(f"{1700000000 + i},{random.choice(SYMBOLS)},{random.uniform(100, 3000):.2f},{random.randint(1, 500)}\n")

rows = [{"id": i, "symbol": random.choice(SYMBOLS), "price": round(random.uniform(100, 3000), 2),
         "qty": random.randint(1, 500), "side": random.choice(["buy", "sell"]), "tags": ["nse", "eq"]}
        for i in range(500_000)]
with open("orders.json", "w") as f:
    json.dump(rows, f)
