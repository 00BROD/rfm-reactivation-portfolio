# Online Retail — RFM & Dormant-Revenue Reactivation

End-to-end analytics project on real UK e-commerce data (UCI Online Retail, 541K rows → 396K clean sale lines).
Raw transactions → SQLite warehouse → RFM segmentation → cohort retention → a ranked, priority-scored **reactivation call-list** → interactive dashboard.

**Headline (stated honestly):** 809 previously-valuable customers have lapsed an average of ~4 months, holding **£1.21M in *lapsed lifetime value*** — that's the *pool*, not the prize. Modelled at a conservative **8% win-back**, the realistically **recoverable** revenue is **~£37K**, delivered as a ranked call list (`output/reactivation_targets.csv`). The dashboard lets you move the win-back rate yourself.

## Live
- **Interactive dashboard:** https://retail-reactivation.vercel.app
- **Tableau Public:** _built from `output/extracts/tableau_flat.csv` via `TABLEAU-PUBLIC-RECIPE.md`_

## Stack
SQLite · SQL (window functions, NTILE) · Python (pandas, numpy, matplotlib) · ECharts. Single self-contained HTML, charts served same-origin (no CDN dependency). Extracts feed Tableau / Power BI.

## Reproduce (clean clone works — source auto-downloads)
```bash
python3 build_db.py                          # auto-downloads source -> data/retail.db (~60s)
sqlite3 data/retail.db < sql/analysis.sql    # SQL showcase (KPIs, Pareto, RFM)
python3 analyze.py                           # RFM, cohorts, reactivation list, charts, metrics.json
python3 build_app.py                          # -> site/index.html (interactive)
open site/index.html
```

## Method, assumptions & limitations
*Stating these up front because a model is only as trustworthy as its caveats.*

**Cleaning**
- Dropped cancellations (`InvoiceNo` starts `C`), non-positive quantity/price, and rows with no `CustomerID`.
- Dropped **non-product service lines** — postage, manual adjustments, bank charges, samples (`POST`, `M`, `DOT`, …). They are not sales; they were inflating revenue and polluting "top products" (~£150K / 1.7%).
- Excluded **wholesale/anomaly line items** (`Quantity ≥ 5000`). Two single orders (80,995 + 74,215 units) alone were ~2.7% of revenue and distorted AOV and top-products.
- These decisions move the headline revenue from £8.91M to **£8.52M** — deliberately, in the direction of truth.

**Definitions**
- **Frequency = distinct purchase _occasions_ (days), not invoices.** A retailer that splits one checkout into many invoices would otherwise look like a loyal repeat buyer (one test account had 34 invoices across 2 days). Using occasions fixes this everywhere.
- **Recency** measured from a snapshot one day after the last invoice in the dataset.
- **RFM** = each of R/F/M scored 1–4 by quartile (`NTILE`); segments are rule-based on those scores.
- **Cohort retention** = % of an acquisition-month cohort that purchases *in* each later month. For a gift retailer (people buy a few times a year) this is a conservative, choppy measure — it under-states "ever returns."

**The reactivation model**
- A customer is a target if dormant ≥ 90 days **and** a top-half lifetime spender (or already "At Risk").
- **Priority = 0.5·monetary + 0.3·frequency + 0.2·(1 − recency)**, all percentile-ranked. Recency is *inverted*: a more recently lapsed customer is a warmer prospect, so less-dormant ranks higher.
- **ROI is illustrative, not a forecast:** one recovered order per reactivation at that customer's own historical AOV, default 8% win-back (email win-back typically converts 1–5%; outbound phone to known customers higher). The weights and threshold are defensible heuristics, **not** statistically validated against a holdout.

**Scope**
- This is **descriptive + heuristic** analytics (segmentation, cohorts, ranking) — not predictive modelling. No train/test, no inference claims.
- Dataset is a single UK gift retailer, 2010–2011. Patterns are real but vintage; treated as a methods showcase, not current market intelligence.

## Layout
```
build_db.py / analyze.py / build_app.py     pipeline (build_dashboard.py = older static version)
sql/analysis.sql                             6 analyst queries (window fns, NTILE, Pareto, RFM)
app_template.html                            interactive dashboard template (data injected at build)
EXECUTIVE-SUMMARY.md                         the written report
TABLEAU-POWERBI-GUIDE.md / -RECIPE.md        BI build kits
output/reactivation_targets.csv              the deliverable: ranked call list
output/{charts,extracts}/                    PNGs + BI-ready CSVs (fact + dims)
```

## Why this exists
One artifact, three jobs: data-analyst portfolio proof, a real agency offer ("find the lapsed revenue in your customer list"), and a prioritization brain for an outbound dialer.

Data: UCI ML Repository — Online Retail (Chen, 2015). Public; no PII beyond anonymized customer IDs.
