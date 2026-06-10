"""
Build the INTERACTIVE dashboard (10/10 pass): ECharts + searchable/sortable call list
+ reactivation-ROI calculator + animated signature counter + OG card + favicon.
Self-contained single HTML (ECharts via CDN). Reads metrics.json + extracts.
"""
import json, pathlib, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT=pathlib.Path("output"); EXT=OUT/"extracts"; SITE=pathlib.Path("site"); SITE.mkdir(exist_ok=True)
m=json.load(open(OUT/"metrics.json"))
monthly=pd.read_csv(EXT/"monthly_revenue.csv")
seg=pd.read_csv(EXT/"segment_summary.csv")
rfm=pd.read_csv(EXT/"rfm_customers.csv")
react=pd.read_csv(OUT/"reactivation_targets.csv")

INK="#16223d"; ACC="#e2574c"; GOLD="#d9a441"; MUT="#7c869c"

# ---- OG card 1200x630 -------------------------------------------------------
fig=plt.figure(figsize=(12,6.3),dpi=100); fig.patch.set_facecolor(INK)
ax=fig.add_axes([0,0,1,1]); ax.axis("off")
ax.text(.06,.78,"CUSTOMER ANALYTICS · RFM SEGMENTATION",color=ACC,fontsize=15,fontweight="bold",family="DejaVu Sans")
ax.text(.06,.60,"Dormant-Revenue\nReactivation",color="white",fontsize=46,fontweight="bold",va="top",linespacing=1.0)
ax.text(.06,.26,f"£{m['react_historical_rev']/1e6:.2f}M idle  ·  {m['react_customers']} win-back customers  ·  {m['customers']:,} analysed",
        color="#cdd6e6",fontsize=18)
ax.text(.06,.13,"SQL · Python · interactive dashboard",color=MUT,fontsize=14)
fig.savefig(SITE/"og.png",facecolor=INK); plt.close()

# ---- data for JS ------------------------------------------------------------
months=monthly.InvoiceMonth.tolist()
mrev=[round(x) for x in monthly.revenue.tolist()]
seg_sorted=seg.sort_values("revenue",ascending=False)
segs=[{"name":r.segment,"rev":round(r.revenue),"cust":int(r.customers)} for r in seg_sorted.itertuples()]
# scatter: [recency, monetary, isTarget]
tgt_ids=set(react.CustomerID.tolist())
pts=[[int(r.recency),round(r.monetary,2),(1 if r.CustomerID in tgt_ids else 0)] for r in rfm.itertuples()]
# call list (sorted by priority desc already)
rows=[[int(r.CustomerID),r.country,int(r.recency),int(r.frequency),round(r.monetary),
       round(r.est_reactivation_value),round(r.priority_score)] for r in react.itertuples()]
# ROI: cumulative est_reactivation_value by priority rank (for slider)
cum=react.est_reactivation_value.cumsum().round().tolist()

DATA=dict(m=m,months=months,mrev=mrev,segs=segs,pts=pts,rows=rows,cum=cum,
          n_targets=len(react),total_idle=round(react.monetary.sum()))
DJSON=json.dumps(DATA,separators=(",",":"))

html=open("app_template.html").read().replace("/*__DATA__*/", "window.D="+DJSON+";")
(SITE/"index.html").write_text(html)
(OUT/"dashboard.html").write_text(html)
print(f"index.html written ({len(html):,} bytes). targets:{len(react)} scatter:{len(pts)}")
