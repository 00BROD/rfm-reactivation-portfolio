# Executive Summary — RFM & Dormant-Revenue Reactivation
**Dataset:** UCI Online Retail · UK-based online gift retailer · 1 Dec 2010 – 9 Dec 2011
**Scope:** 397,884 clean transaction lines · 18,532 orders · 4,338 customers · £8.9M revenue

---

## The one-line finding
**646 previously-valuable customers have gone silent for ~120 days, representing ~£1.0M of historical revenue.** They are warm, proven buyers who simply stopped — the single highest-ROI list a sales team can work.

---

## 1. Headline KPIs
| Metric | Value |
|---|---|
| Revenue | **£8,911,408** |
| Orders | 18,532 |
| Customers | 4,338 |
| Avg order value | **£480.87** |
| Revenue from top 10% of customers | **61%** |
| Revenue from top 20% of customers | **75%** |

**Read:** revenue is heavily concentrated. A small base of high-value customers carries the business, so *retaining and reactivating customers beats chasing new ones* on pure ROI.

## 2. Seasonality
Revenue is steady (~£500–680k/mo) Jan–Aug, then ramps hard into the holidays: **Sep £953k → Oct £1.04M → Nov £1.16M** (Dec partial). A gifting catalogue with a Q4 spike — reactivation campaigns should fire **August/September**, ahead of the peak, not during it.

## 3. RFM segmentation
Every customer scored 1–4 on **R**ecency, **F**requency, **M**onetary (quartiles), then bucketed:

| Segment | Customers | Revenue | Avg recency | Avg orders |
|---|---|---|---|---|
| **Champions** | 1,319 | £6.51M | 17 d | 9.4 |
| **At Risk (was valuable)** | 646 | £1.04M | 119 d | 4.2 |
| Lapsed / Low | 1,504 | £0.77M | 187 d | 1.3 |
| Loyal | 610 | £0.50M | 23 d | 2.2 |
| Recent / New | 259 | £0.09M | 27 d | 1.0 |

**Champions** (30% of base) drive 73% of revenue — protect at all costs. **At Risk** is the opportunity: they bought 4+ times, spent real money, then disappeared four months ago.

## 4. The reactivation list (the actionable output)
Filtering for *dormant (≥90 days) AND historically valuable (top-half spenders)* yields **807 target customers worth £1.32M in past revenue**, each scored:

`priority = 0.50·monetary + 0.30·frequency + 0.20·recency` (percentile-ranked)

Delivered as `output/reactivation_targets.csv` — a ranked call/email list with customer ID, country, days dormant, order count, lifetime spend, and estimated next-order value. **This is a sales team's Monday-morning dial list.**

## 5. Recommendations
1. **Reactivate before you acquire.** 807 warm targets at £1.32M historical value cost far less to win back than net-new customers.
2. **Time it for August.** Hit dormant buyers ahead of the Sep–Nov ramp.
3. **Tier the outreach by priority score** — phone the top decile, email the rest.
4. **Defend Champions** with continuity/loyalty before they slide into At-Risk.

---
*Method: raw `.xlsx` → SQLite (cleaning, indexing) → SQL analysis + Python RFM (pandas) → charts (matplotlib) → dashboard. Reproducible end-to-end via `build_db.py` → `analyze.py` → `build_dashboard.py`.*
