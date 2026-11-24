import json

with open("orders.json") as f:
    rows = json.load(f)
for r in rows:
    r["value"] = round(r["price"] * r["qty"], 2)
text = json.dumps(rows)
print(len(rows), len(text))
