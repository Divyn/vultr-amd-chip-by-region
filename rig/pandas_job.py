import pandas as pd

df = pd.read_csv("trades.csv")
df["value"] = df["price"] * df["qty"]
out = df.groupby("symbol").agg(trades=("qty", "size"), qty=("qty", "sum"), value=("value", "sum"), avg=("price", "mean"))
out.sort_values("value", ascending=False).to_csv("/tmp/summary.csv")
print(len(df))
