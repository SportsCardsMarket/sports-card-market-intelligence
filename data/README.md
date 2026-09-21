# Live Market Dataset

This directory is reserved for the weekly completed-sale dataset and derived market summaries.

The production target is up to **100,000 recent completed sales**, subject to eBay Marketplace Insights access, API limits, and the available 90-day sales-history window.

The refresh workflow runs weekly through GitHub Actions. It does not fabricate missing transactions: if the source does not return enough eligible sales, the summary reports the actual number collected.

Core outputs:
- `market-sales.csv` — normalized transaction-level records
- `market-summary.json` — current aggregate statistics

Future dashboard layers can derive player/card pages, price trends, liquidity, grading spreads, anomaly detection, and market movers from this dataset.
