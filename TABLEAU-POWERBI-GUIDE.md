# Tableau & Power BI — Build Kit

**Straight talk on what's agentic vs. manual.** Tableau Desktop and Power BI Desktop are GUI apps — I can't headlessly *render* a `.twb`/`.pbix` dashboard the way I can a web page, and faking a binary workbook risks shipping a file that won't open (portfolio-killer). So I did the part that's 90% of the work and 100% reliable: **clean, analysis-ready extracts + the exact fields, measures, and chart recipe.** Loading them is a 10-minute drag-drop. The self-contained `output/dashboard.html` already gives you a live dashboard with zero tools.

## Extracts (in `output/extracts/`)
| File | Grain | Use as |
|---|---|---|
| `fact_sales.csv` | one row per line item | **fact table** |
| `rfm_customers.csv` | one row per customer (R,F,M,score,segment) | **customer dimension** |
| `monthly_revenue.csv` | one row per month | pre-agg trend |
| `segment_summary.csv` | one row per segment | segment bars |
| `country_revenue.csv` | one row per country | map / geo |
| `output/reactivation_targets.csv` | ranked target list | the call-list table |

Model: join `fact_sales[CustomerID]` → `rfm_customers[CustomerID]` (many-to-one).

---

## Power BI (Desktop, free)
1. **Get Data → Text/CSV** → load `fact_sales.csv` and `rfm_customers.csv`.
2. **Model view** → relate `fact_sales[CustomerID]` → `rfm_customers[CustomerID]`.
3. Paste these **DAX measures**:
```DAX
Revenue            = SUM(fact_sales[Revenue])
Orders             = DISTINCTCOUNT(fact_sales[InvoiceNo])
Customers          = DISTINCTCOUNT(fact_sales[CustomerID])
AOV                = DIVIDE([Revenue],[Orders])
Dormant Revenue    = CALCULATE(SUM(rfm_customers[monetary]),
                       rfm_customers[segment]="At Risk (was valuable)")
Reactivation Count = CALCULATE(DISTINCTCOUNT(rfm_customers[CustomerID]),
                       rfm_customers[recency]>=90, rfm_customers[M]>=3)
```
4. Visuals: KPI cards (Revenue, AOV, Dormant Revenue) · line chart Revenue by `InvoiceMonth` · bar Revenue by `segment` · scatter `recency` vs `monetary` colored by `segment` · table of `reactivation_targets`.

## Tableau (Public is free)
1. **Connect → Text file** → `fact_sales.csv`; add `rfm_customers.csv`, relate on `CustomerID`.
2. **Calculated fields:**
```
AOV          : SUM([Revenue]) / COUNTD([InvoiceNo])
Is Dormant   : IF [Recency] >= 90 AND [M] >= 3 THEN "Reactivate" ELSE "Active" END
```
3. Sheets → assemble on a dashboard: KPI text tiles · `InvoiceMonth` line · `segment` bar · `Recency` vs `monetary` scatter (color = `Is Dormant`) · target-list table.
4. Tableau Public publish = a shareable live link for your portfolio.

**Tip:** the `output/charts/*.png` match these exactly — use them as design reference so the BI version looks intentional.
