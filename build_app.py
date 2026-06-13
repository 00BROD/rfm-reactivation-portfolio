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

INK="#1B1713"; ACC="#C0532E"; GOLD="#A98140"; MUT="#9B9080"; CREAM="#FBF3E6"

# ---- OG card 1200x630 (warm editorial) --------------------------------------
fig=plt.figure(figsize=(12,6.3),dpi=100); fig.patch.set_facecolor(INK)
ax=fig.add_axes([0,0,1,1]); ax.axis("off"); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.add_patch(plt.Rectangle((0,0),1,1,color="#2C2620",zorder=0))   # warm panel
ax.add_patch(plt.Rectangle((0,0),.012,1,color=ACC,zorder=1))      # terracotta spine
ax.text(.07,.78,"CUSTOMER ANALYTICS · RFM SEGMENTATION",color=ACC,fontsize=15,fontweight="bold",family="DejaVu Sans")
ax.text(.07,.60,"Dormant-Revenue\nReactivation",color=CREAM,fontsize=48,fontweight="bold",va="top",linespacing=1.0,family="DejaVu Serif")
ax.text(.07,.26,f"£{m['react_historical_rev']/1e6:.2f}M idle   ·   {m['react_customers']} win-back customers   ·   {m['customers']:,} analysed",
        color="#D8C9B6",fontsize=18)
ax.text(.07,.13,"SQL · Python · interactive dashboard",color=MUT,fontsize=14)
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

cohorts=json.load(open(OUT/"cohorts.json"))
pareto=json.load(open(OUT/"pareto.json"))
# per-point segment for cross-filtering: [recency, monetary, isTarget, segIdx]
seg_names=[s["name"] for s in segs]
seg_idx={n:i for i,n in enumerate(seg_names)}
pts=[[int(r.recency),round(r.monetary,2),(1 if r.CustomerID in tgt_ids else 0),seg_idx[r.segment]]
     for r in rfm.itertuples()]
# call-list rows get segment too
seg_by_id=dict(zip(rfm.CustomerID,rfm.segment))
rows=[[int(r.CustomerID),r.country,int(r.recency),int(r.frequency),round(r.monetary),
       round(r.est_reactivation_value),round(r.priority_score),seg_by_id.get(r.CustomerID,"")] for r in react.itertuples()]

DATA=dict(m=m,months=months,mrev=mrev,segs=segs,pts=pts,rows=rows,cum=cum,
          n_targets=len(react),total_idle=round(react.monetary.sum()),
          cohorts=cohorts,pareto=pareto,seg_names=seg_names)
DJSON=json.dumps(DATA,separators=(",",":"))

# vendor echarts locally (same-origin) so blocked CDNs can't blank charts in a live demo
ECH=SITE/"echarts.min.js"
if not ECH.exists():
    import urllib.request
    print("fetching echarts.min.js (one-time)...",flush=True)
    urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js",ECH)

html=open("app_template.html").read().replace("/*__DATA__*/", "window.D="+DJSON+";")
(SITE/"index.html").write_text(html)
(OUT/"dashboard.html").write_text(html)
print(f"index.html written ({len(html):,} bytes). targets:{len(react)} scatter:{len(pts)}")
