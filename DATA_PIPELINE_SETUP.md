# Sports Card Market Intelligence

Portfolio dashboard for multi-sport card market research.

## Live sales data

The dashboard can ingest verified completed-sale records through **The Card API** and calculate:

- Median / average sale price
- Minimum / maximum observed sale
- Transaction volume
- Recent transaction table
- Card-level market snapshots
- Future 7D / 30D momentum and liquidity metrics

The Card API documentation: https://www.thecardapi.com/docs

### GitHub Actions setup

Add this repository secret:

- **Name:** `THE_CARD_API_KEY`
- **Value:** your private The Card API key

Do not commit the key to the repository.

The current starter integration tracks 10 cards and queries a 3-day window. The Card API's free plan is intended for personal/evaluation use and does not permit persistent local storage; use a paid plan for the GitHub-persisted dataset architecture used by this project. The Starter plan currently provides 10,000 sales/day and 14-day lookback. The dashboard stores normalized transaction data and derived summaries for the portfolio site.

## Architecture

**The Card API → GitHub Actions → Python normalization → JSON market dataset → GitHub Pages dashboard**

The dashboard keeps asking prices and completed sales separate so a listing price is never presented as a transaction value.

## Important

Transaction records are supplied as-is by the data provider. The dashboard describes them as **observed sale prices**, not guaranteed appraisals or investment advice.
