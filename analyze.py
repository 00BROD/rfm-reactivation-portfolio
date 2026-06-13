"""
RFM + Dormant-Revenue Reactivation analysis.
Reads data/retail.db -> writes charts, per-customer RFM, reactivation target list,
metrics.json, and analysis-ready extracts for Tableau / Power BI.
"""
import sqlite3, json, pathlib
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = pathlib.Path("output"); OUT.mkdir(exist_ok=True)
EXT = pathlib.Path("output/extracts"); EXT.mkdir(exist_ok=True)
CHT = pathlib.Path("output/charts");   CHT.mkdir(exist_ok=True)
con = sqlite3.connect("data/retail.db")

INK="#1b2a4a"; ACC="#e2574c"; GOLD="#d9a441"; MUT="#8a93a6"
plt.rcParams.update({"font.size":13,"axes.edgecolor":MUT,"axes.grid":True,
    "grid.color":"#eceef2","grid.linewidth":.8,"axes.spines.top":False,"axes.spines.right":False,
    "font.family":"DejaVu Sans","axes.titlepad":12,"figure.dpi":100,"savefig.bbox":"tight"})

# ---- pull base frames -------------------------------------------------------
sales = pd.read_sql("SELECT * FROM sales", con, parse_dates=["InvoiceDate"])
snapshot = sales.InvoiceDate.max() + pd.Timedelta(days=1)

# ---- RFM --------------------------------------------------------------------
rfm = sales.groupby("CustomerID").agg(
    recency  =("InvoiceDate", lambda s:(snapshot - s.max()).days),
    # frequency = distinct purchase OCCASIONS (days), not invoices — avoids same-day
    # invoice-splitting inflating loyalty (e.g. a test account with 34 invoices in 2 days)
    frequency=("InvoiceDate", lambda s: s.dt.date.nunique()),
    monetary =("Revenue", "sum"),
    last_purchase=("InvoiceDate","max"),
    country  =("Country", lambda s:s.mode().iat[0]),
).reset_index()

rfm["R"]=pd.qcut(rfm.recency, 4, labels=[4,3,2,1]).astype(int)      # recent=4
rfm["F"]=pd.qcut(rfm.frequency.rank(method="first"),4,labels=[1,2,3,4]).astype(int)
rfm["M"]=pd.qcut(rfm.monetary, 4, labels=[1,2,3,4]).astype(int)
rfm["RFM"]=rfm.R*100+rfm.F*10+rfm.M

def segment(x):
    r,f,m=x.R,x.F,x.M
    if r>=3 and f>=3 and m>=3: return "Champions"
    if r>=3 and f>=2:          return "Loyal"
    if r>=3:                   return "Recent / New"
    if r<=2 and f>=3:          return "At Risk (was valuable)"
    return "Lapsed / Low"
rfm["segment"]=rfm.apply(segment, axis=1)
rfm.to_csv(EXT/"rfm_customers.csv", index=False)

# ---- Reactivation target list (the dialer brain + agency deliverable) -------
# Dormant (recency high) but historically valuable (M>=3 or was a frequent buyer).
react = rfm[(rfm.segment=="At Risk (was valuable)") |
            ((rfm.recency>=90) & (rfm.M>=3))].copy()
# Priority = value × win-back likelihood. Recency is INVERTED: a more recently
# lapsed customer is a warmer, more reachable prospect than one gone a year — so
# LESS dormant scores higher (1 - recency_rank), not more.
react["priority_score"]=(react.monetary.rank(pct=True)*0.5
                        +react.frequency.rank(pct=True)*0.3
                        +(1-react.recency.rank(pct=True))*0.2)*100
react=react.sort_values("priority_score", ascending=False)
react["est_reactivation_value"]=(react.monetary/react.frequency).round(2)  # ~avg order value
react[["CustomerID","country","recency","frequency","monetary",
       "est_reactivation_value","priority_score","last_purchase"]] \
     .to_csv(OUT/"reactivation_targets.csv", index=False)

# ---- analysis-ready extracts for Tableau / Power BI -------------------------
monthly = pd.read_sql("""SELECT InvoiceMonth, ROUND(SUM(Revenue),2) revenue,
        COUNT(DISTINCT InvoiceNo) orders, COUNT(DISTINCT CustomerID) customers
        FROM sales GROUP BY InvoiceMonth ORDER BY InvoiceMonth""", con)
monthly.to_csv(EXT/"monthly_revenue.csv", index=False)
seg = rfm.groupby("segment").agg(customers=("CustomerID","size"),
        revenue=("monetary","sum"), avg_recency=("recency","mean"),
        avg_orders=("frequency","mean")).round(1).reset_index()
seg.to_csv(EXT/"segment_summary.csv", index=False)
country = pd.read_sql("""SELECT Country, ROUND(SUM(Revenue),2) revenue,
        COUNT(DISTINCT CustomerID) customers FROM sales
        GROUP BY Country ORDER BY revenue DESC""", con)
country.to_csv(EXT/"country_revenue.csv", index=False)
# fact table (star-schema friendly for PBI/Tableau)
sales[["InvoiceNo","InvoiceDate","InvoiceMonth","CustomerID","Country",
       "StockCode","Description","Quantity","UnitPrice","Revenue"]] \
     .to_csv(EXT/"fact_sales.csv", index=False)

# ---- charts -----------------------------------------------------------------
# 1 monthly revenue
fig,ax=plt.subplots(figsize=(9.5,4.4))
m=monthly.copy(); m["revenue"]/=1e3
ax.plot(m.InvoiceMonth, m.revenue, marker="o", color=INK, lw=2)
ax.fill_between(range(len(m)), m.revenue, color=INK, alpha=.06)
ax.set_title("Monthly Revenue (£000s)", color=INK, fontweight="bold", loc="left")
ax.set_xticks(range(len(m))); ax.set_xticklabels(m.InvoiceMonth, rotation=45, ha="right")
plt.tight_layout(); plt.savefig(CHT/"monthly_revenue.png", dpi=200); plt.close()

# 2 segment revenue
s=seg.sort_values("revenue")
fig,ax=plt.subplots(figsize=(9.5,4.4))
cols=[ACC if x=="At Risk (was valuable)" else (GOLD if x=="Champions" else MUT) for x in s.segment]
ax.barh(s.segment, s.revenue/1e6, color=cols)
ax.set_title("Revenue by RFM Segment (£M)", color=INK, fontweight="bold", loc="left")
for i,(v,c) in enumerate(zip(s.revenue/1e6,s.customers)):
    ax.text(v+.05,i,f"£{v:.1f}M · {int(c)} cust", va="center", fontsize=11, color=INK)
ax.set_xlim(0, s.revenue.max()/1e6*1.25)
plt.tight_layout(); plt.savefig(CHT/"segment_revenue.png", dpi=200); plt.close()

# 3 RFM scatter (recency vs monetary, dormant-value highlighted)
fig,ax=plt.subplots(figsize=(10,5))
base=rfm[rfm.segment!="At Risk (was valuable)"]
ax.scatter(base.recency, base.monetary, s=14, color=MUT, alpha=.35, label="Other")
ax.scatter(react.recency, react.monetary, s=20, color=ACC, alpha=.8, label="Reactivation target")
ax.set_yscale("log"); ax.set_xlabel("Days since last purchase (recency)")
ax.set_ylabel("Lifetime revenue (£, log)")
ax.set_title("Dormant ≠ Worthless: high-value customers gone quiet",
             color=INK, fontweight="bold", loc="left")
ax.legend(frameon=False)
plt.tight_layout(); plt.savefig(CHT/"rfm_scatter.png", dpi=200); plt.close()

# 4 country mix
c=country.head(6).iloc[::-1]
fig,ax=plt.subplots(figsize=(9.5,4.4))
ax.barh(c.Country, c.revenue/1e6, color=INK)
ax.set_title("Top Markets by Revenue (£M)", color=INK, fontweight="bold", loc="left")
plt.tight_layout(); plt.savefig(CHT/"country_revenue.png", dpi=200); plt.close()

# ---- metrics.json (feeds dashboard + exec summary) --------------------------
tot=float(sales.Revenue.sum())
react_rev=float(react.monetary.sum())                 # lapsed lifetime value (pool, NOT recoverable)
RECOVER_RATE=0.08                                     # defensible blended win-back rate (see README)
recoverable=float(react.est_reactivation_value.sum())*RECOVER_RATE   # one order each @ rate
# Pareto computed, not hardcoded
cv=rfm.monetary.sort_values(ascending=False).cumsum()/rfm.monetary.sum()
top10=int(round(100*cv.iloc[int(len(cv)*0.10)-1])); top20=int(round(100*cv.iloc[int(len(cv)*0.20)-1]))
metrics=dict(
  revenue=round(tot), orders=int(sales.InvoiceNo.nunique()),
  customers=int(sales.CustomerID.nunique()),
  aov=round(tot/sales.InvoiceNo.nunique(),2),
  date_min=str(sales.InvoiceDate.min().date()), date_max=str(sales.InvoiceDate.max().date()),
  top10_pct_rev=top10, top20_pct_rev=top20,
  react_customers=int(len(react)),
  react_historical_rev=round(react_rev),               # = lapsed LTV pool
  recoverable_est=round(recoverable),
  recover_rate=int(RECOVER_RATE*100),
  react_avg_dormant_days=int(react.recency.mean()),
  champions_rev=round(float(rfm.loc[rfm.segment=="Champions","monetary"].sum())),
  segments=seg.to_dict("records"),
)
json.dump(metrics, open(OUT/"metrics.json","w"), indent=2)
con.close()
print(json.dumps(metrics, indent=2))
print(f"\nreactivation list: {len(react)} customers, £{react_rev:,.0f} historical revenue")
print("extracts:", [p.name for p in EXT.glob('*.csv')])
print("charts:",   [p.name for p in CHT.glob('*.png')])
