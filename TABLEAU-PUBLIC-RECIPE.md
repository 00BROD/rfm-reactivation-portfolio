# Tableau Public — 10-Minute Build → Live Link

You have **Tableau Public Desktop installed**. One flat file does the whole thing — no joins, no modeling.
**Import file:** `output/extracts/tableau_flat.csv` (397,884 rows; every sale already tagged with its customer's RFM segment + `IsReactivationTarget`).

## Connect (1 min)
1. Open Tableau Public → **Connect → Text File** → pick `tableau_flat.csv`.
2. Check types: `InvoiceDate`=Date, `Revenue`/`monetary`=number, `CustomerID`/`segment`/`Country`=dimensions. Go to **Sheet 1**.

## Two calculated fields (Analysis → Create Calculated Field)
```
AOV   :  SUM([Revenue]) / COUNTD([Invoice No])
```
(`IsReactivationTarget` already exists in the data — no calc needed.)

## Four sheets (~2 min each)

**Sheet "Revenue Trend"** — Columns: `InvoiceMonth` (or `MONTH(InvoiceDate)` continuous) · Rows: `SUM(Revenue)` · mark = Line.

**Sheet "Segment Revenue"** — Columns: `SUM(monetary)` · Rows: `segment` (sort desc) · Color: `segment` · mark = Bar. Drag `IsReactivationTarget` to Color to make the "Reactivate" segment pop red.

**Sheet "Dormant Scatter"** — Columns: `AVG(recency)` · Rows: `SUM(monetary)` · Detail: `CustomerID` · Color: `IsReactivationTarget` · mark = Circle. Right-click Rows axis → Logarithmic.

**Sheet "Call List"** — Rows: `CustomerID`, `Country`, `segment` · Text: `SUM(monetary)`, `AVG(recency)`, `MAX(frequency)`. Filter `IsReactivationTarget = Reactivate`. Sort by `monetary` desc → that's your dial list.

## Dashboard + publish (2 min)
1. **New Dashboard** → drag the 4 sheets in (size = Automatic).
2. Add 3 KPI text tiles up top: Revenue £8.9M · AOV £481 · Dormant revenue £1.0M.
3. Title: **"RFM & Dormant-Revenue Reactivation"**.
4. **File → Save to Tableau Public** → login → **your live `public.tableau.com` link.**

## For the résumé
> Built an RFM customer-segmentation model on 540K e-commerce transactions (SQL + Python), surfaced an **807-customer / £1.3M dormant-revenue reactivation list**, and shipped an interactive Tableau Public dashboard. *Skills: SQL, Python (pandas), Tableau, customer analytics, RFM.*

Live HTML version (already deployed): https://retail-reactivation.vercel.app
