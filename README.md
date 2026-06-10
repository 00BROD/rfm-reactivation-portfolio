# Online Retail — RFM & Dormant-Revenue Reactivation

End-to-end analytics project on real UK e-commerce data (UCI Online Retail, 541k rows).
Raw transactions → SQL warehouse → RFM segmentation → a ranked customer **reactivation call-list** → dashboard.

**Headline:** 646 previously-valuable customers went dormant ~120 days, worth **£1.0M** of historical revenue — surfaced as an 807-row, priority-scored target list (`output/reactivation_targets.csv`).

## Stack
SQLite · Python (pandas, numpy, matplotlib) · SQL · self-contained HTML dashboard. Extracts feed Tableau / Power BI.

## Reproduce
```bash
python3 build_db.py          # Online Retail.xlsx -> data/retail.db  (~60s, one-time)
sqlite3 data/retail.db < sql/analysis.sql   # SQL showcase (KPIs, Pareto, RFM)
python3 analyze.py           # RFM, reactivation list, charts, extracts, metrics.json
python3 build_dashboard.py   # -> output/dashboard.html
open output/dashboard.html
```

## Layout
```
build_db.py / analyze.py / build_dashboard.py   pipeline
sql/analysis.sql                                 6 analyst queries (window fns, NTILE, Pareto, RFM)
EXECUTIVE-SUMMARY.md                             the report
TABLEAU-POWERBI-GUIDE.md                         BI build kit (DAX + calc fields + extracts)
output/dashboard.html                            live dashboard (zero deps)
output/reactivation_targets.csv                  the deliverable: ranked call list
output/charts/                                   4 PNGs
output/extracts/                                 BI-ready CSVs (fact + dims)
```

## Why this exists
Three jobs, one artifact: (1) data-analyst portfolio proof, (2) a real agency offer — "find the dormant revenue in your customer list", (3) a prioritization brain for an outbound dialer.

Data: UCI ML Repository — Online Retail (Chen, 2015). Public dataset, no PII beyond anonymized customer IDs.
