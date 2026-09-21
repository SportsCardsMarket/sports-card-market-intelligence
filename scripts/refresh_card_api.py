import json, os, time
from datetime import date, timedelta
from pathlib import Path
import requests

BASE = "https://thecardapi.com/api/v1/market/sales"
ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "data" / "card-queries.json").read_text())
key = os.environ.get("THE_CARD_API_KEY")
if not key:
    raise SystemExit("THE_CARD_API_KEY is required")

headers = {"x-market-api-key": key}
end = date.today()
start = end - timedelta(days=int(cfg.get("lookback_days", 3)))
all_sales = []

for card in cfg["cards"]:
    params = {
        "q": card["query"],
        "category": "sports",
        "date_from": start.isoformat(),
        "date_to": end.isoformat(),
        "limit": min(int(cfg.get("limit_per_card", 50)), 1000),
    }
    r = requests.get(BASE, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    payload = r.json()
    for row in payload.get("data", []):
        price = row.get("price")
        if isinstance(price, (int, float)) and price > 0:
            row["tracked_card"] = card["name"]
            all_sales.append(row)
    time.sleep(0.15)

# Deduplicate by source sale ID.
dedup = {}
for row in all_sales:
    dedup[str(row.get("id"))] = row
sales = list(dedup.values())
sales.sort(key=lambda x: (x.get("sale_date") or "", x.get("sold_at") or ""), reverse=True)

summary_cards = []
for card in cfg["cards"]:
    vals = [float(x["price"]) for x in sales if x.get("tracked_card") == card["name"]]
    vals.sort()
    if not vals:
        summary_cards.append({
            "name": card["name"], "query": card["query"], "sales_count": 0,
            "median_sale": None, "average_sale": None, "min_sale": None,
            "max_sale": None, "updated_at": end.isoformat()
        })
        continue
    n = len(vals)
    median = vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2
    summary_cards.append({
        "name": card["name"], "query": card["query"], "sales_count": n,
        "median_sale": round(median, 2), "average_sale": round(sum(vals)/n, 2),
        "min_sale": round(min(vals), 2), "max_sale": round(max(vals), 2),
        "updated_at": end.isoformat()
    })

out = {
    "source": "The Card API",
    "source_url": "https://www.thecardapi.com/",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "lookback_days": int(cfg.get("lookback_days", 3)),
    "sales_loaded": len(sales),
    "cards": summary_cards,
    "sales": sales
}
(ROOT / "data" / "card-market-live.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
print(f"Loaded {len(sales)} verified sale records across {len(cfg['cards'])} tracked cards.")
