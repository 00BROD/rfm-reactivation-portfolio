# Executive Summary: RFM & Dormant-Revenue Reactivation
**Dataset:** UCI Online Retail · UK online gift retailer · Dec 2010 to Dec 2011
**Scope:** 396,335 clean sale lines · 18,400 orders · 4,333 customers · £8.52M revenue
*(After excluding cancellations, non-product service lines, and two wholesale-scale anomaly orders. See Method & Limitations.)*

---

## The one-line finding
**647 previously-valuable customers have lapsed ~119 days, holding £0.91M in lifetime value — and the broader win-back list of 809 customers holds £1.21M.** That is the *pool*, not the prize: modelled at a conservative 8% win-back, the realistically **recoverable** revenue is **~£37K**. They are warm, proven buyers who simply stopped — the highest-ROI list a sales team can work.

---

## 1. Headline KPIs
| Metric | Value |
|---|---|
| Revenue | **£8,515,413** |
| Orders | 18,400 |
| Customers | 4,333 |
| Avg order value | **£462.79** |
| Revenue from top 10% of customers | **60%** |
| Revenue from top 20% of customers | **74%** |

**Read:** revenue is heavily concentrated. A small base of high-value customers carries the business, so *retaining and reactivating customers beats chasing new ones* on pure ROI.

## 2. Seasonality
Revenue is steady (~£500–680K/mo) through spring and summer, then ramps hard into the holidays: **Sep £941K → Oct £1.01M → Nov £1.14M** (Dec partial). A gifting catalogue with a Q4 spike, so reactivation campaigns should fire **August/September**, ahead of the peak, not during it.

## 3. RFM segmentation
Every customer scored 1–4 on **R**ecency, **F**requency, **M**onetary by quartile (NTILE). Frequency = distinct purchase *occasions* (days), not invoices, so invoice-splitting can't fake loyalty.

| Segment | Customers | Revenue | Avg recency | Avg occasions |
|---|---|---|---|---|
| **Champions** | 1,309 | £6.36M | 17 d | 8.3 |
| **At Risk (was valuable)** | 647 | £0.91M | 119 d | 3.8 |
| Lapsed / Low | 1,505 | £0.79M | 187 d | 1.2 |
| Loyal | 614 | £0.35M | 23 d | 2.1 |
| Recent / New | 258 | £0.10M | 27 d | 1.0 |

**Champions** (~30% of base) drive ~75% of revenue: protect at all costs. **At Risk** is the opportunity — they bought several times, spent real money, then disappeared ~4 months ago.

## 4. The reactivation list (the actionable output)
Filtering for *dormant (≥90 days) AND historically valuable (top-half spenders)* yields **809 target customers**, each scored:

`priority = 0.50·monetary + 0.30·frequency + 0.20·(1 − recency)` (percentile-ranked)

Recency is **inverted**: a customer who lapsed last month is a warmer, more reachable prospect than one gone a year, so less-dormant ranks higher. Delivered as `output/reactivation_targets.csv` — a ranked call/email list with customer ID, country, days dormant, purchase occasions, lifetime spend, and estimated next-order value. **This is a sales team's Monday-morning dial list.**

## 5. Recommendations
1. **Reactivate before you acquire.** 809 warm targets cost far less to win back than net-new customers; even a conservative 8% recovers ~£37K at near-zero acquisition cost.
2. **Time it for August.** Hit lapsed buyers ahead of the Sep–Nov ramp.
3. **Tier the outreach by priority score.** Phone the top decile, email the rest.
4. **Defend Champions** with continuity/loyalty before they slide into At-Risk.

## Method & limitations (the honest part)
- **Cleaning changes the totals on purpose:** removing service lines (postage/manual/fees, ~£150K) and two wholesale-scale anomaly orders (~£245K) moves revenue from £8.91M to £8.52M, toward truth.
- **The £1.21M is lapsed lifetime value, not recoverable cash.** Recoverable is modelled (one order each at historical AOV × win-back rate) and shown as a live, adjustable figure on the dashboard. Default 8% is deliberately conservative (email win-back typically 1–5%).
- **Heuristic, not predictive.** Segment cutoffs and priority weights are defensible rules, not validated against a holdout. No statistical inference is claimed.
- **Vintage data.** A single UK retailer, 2010–2011; treat as a methods showcase, not current market intelligence.

---
*Pipeline: raw `.xlsx` → SQLite (cleaning, indexing) → SQL + Python RFM/cohorts (pandas) → ECharts dashboard. Reproducible end-to-end (source auto-downloads): `build_db.py` → `analyze.py` → `build_app.py`.*
