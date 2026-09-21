import json, os, statistics
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
LIMIT = int(os.getenv("SALES_LIMIT", "100000"))

def get_token():
    token = os.getenv("EBAY_MARKETPLACE_INSIGHTS_TOKEN")
    if token:
        return token
    client_id, secret = os.getenv("EBAY_CLIENT_ID"), os.getenv("EBAY_CLIENT_SECRET")
    if not client_id or not secret:
        raise RuntimeError("Missing eBay credentials. Add EBAY_CLIENT_ID, EBAY_CLIENT_SECRET and/or EBAY_MARKETPLACE_INSIGHTS_TOKEN to GitHub Actions secrets.")
    r = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        data={"grant_type":"client_credentials","scope":"https://api.ebay.com/oauth/api_scope"},
        auth=(client_id, secret), timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def fetch_sales(token):
    # Marketplace Insights is a limited-release eBay API and access must be granted by eBay.
    url = "https://api.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search"
    headers = {"Authorization": f"Bearer {token}", "Accept":"application/json"}
    rows, offset = [], 0
    while len(rows) < LIMIT:
        params = {"limit": min(200, LIMIT-len(rows)), "offset": offset}
        r = requests.get(url, headers=headers, params=params, timeout=60)
        r.raise_for_status()
        payload = r.json()
        batch = payload.get("itemSales") or payload.get("item_sales") or []
        if not batch: break
        rows.extend(batch)
        offset += len(batch)
        if len(batch) < params["limit"]: break
    return rows[:LIMIT]

def normalize(rows):
    out=[]
    for x in rows:
        price=x.get("price") or {}
        out.append({
            "sale_date": x.get("itemEndDate") or x.get("item_end_date"),
            "title": x.get("title",""),
            "item_id": x.get("itemId") or x.get("item_id"),
            "price": price.get("value"),
            "currency": price.get("currency"),
            "condition": x.get("condition"),
            "category_id": x.get("categoryId") or x.get("category_id"),
            "listing_type": x.get("listingType") or x.get("listing_type"),
        })
    return pd.DataFrame(out)

def main():
    rows=fetch_sales(get_token())
    df=normalize(rows)
    if df.empty: raise RuntimeError("eBay returned no sales.")
    df["price"]=pd.to_numeric(df["price"], errors="coerce")
    df=df.dropna(subset=["price"]).drop_duplicates(subset=["item_id"], keep="first")
    df.to_csv(DATA/"market-sales.csv", index=False)
    summary={
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sales_loaded": int(len(df)),
        "median_sale_price": float(df["price"].median()),
        "average_sale_price": float(df["price"].mean()),
        "total_observed_value": float(df["price"].sum()),
        "unique_items": int(df["item_id"].nunique()),
    }
    (DATA/"market-summary.json").write_text(json.dumps(summary, indent=2))

if __name__=="__main__":
    main()
