"""Render a self-contained HTML dashboard from metrics.json + reactivation_targets.csv.
Opens in any browser, zero dependencies, charts embedded as base64."""
import json, base64, pathlib, pandas as pd

OUT=pathlib.Path("output"); CHT=OUT/"charts"
m=json.load(open(OUT/"metrics.json"))
react=pd.read_csv(OUT/"reactivation_targets.csv").head(15)

def img(p):
    return "data:image/png;base64,"+base64.b64encode((CHT/p).read_bytes()).decode()

def gbp(x): return f"£{x:,.0f}"
rows="".join(
  f"<tr><td>{int(r.CustomerID)}</td><td>{r.country}</td><td>{int(r.recency)}d</td>"
  f"<td>{int(r.frequency)}</td><td>{gbp(r.monetary)}</td>"
  f"<td>{gbp(r.est_reactivation_value)}</td>"
  f"<td><b>{r.priority_score:.0f}</b></td></tr>"
  for r in react.itertuples())

seg_rows="".join(
  f"<tr><td>{s['segment']}</td><td>{int(s['customers'])}</td>"
  f"<td>{gbp(s['revenue'])}</td><td>{s['avg_recency']:.0f}d</td>"
  f"<td>{s['avg_orders']:.1f}</td></tr>"
  for s in sorted(m['segments'], key=lambda x:-x['revenue']))

html=f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Online Retail — RFM & Dormant-Revenue Reactivation</title>
<style>
:root{{--ink:#1b2a4a;--acc:#e2574c;--gold:#d9a441;--mut:#8a93a6;--bg:#f6f7f9;--card:#fff}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;
color:var(--ink);background:var(--bg)}}
.wrap{{max-width:1080px;margin:0 auto;padding:32px 22px 64px}}
header h1{{font-size:26px;margin:0 0 4px}}header p{{color:var(--mut);margin:0}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}}
.kpi{{background:var(--card);border:1px solid #e7eaef;border-radius:12px;padding:16px}}
.kpi .v{{font-size:24px;font-weight:700}}.kpi .l{{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.04em}}
.kpi.hot{{background:var(--ink);color:#fff}}.kpi.hot .l{{color:#aeb8cc}}
.card{{background:var(--card);border:1px solid #e7eaef;border-radius:12px;padding:20px;margin:16px 0}}
.card h2{{font-size:16px;margin:0 0 12px}}
img{{width:100%;border-radius:8px;display:block}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{text-align:left;padding:7px 9px;border-bottom:1px solid #eef0f3}}
th{{color:var(--mut);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.03em}}
tbody tr:hover{{background:#fafbfc}}
.pill{{display:inline-block;background:#fdecea;color:var(--acc);padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600}}
.lead{{font-size:17px;line-height:1.5}}.lead b{{color:var(--acc)}}
footer{{color:var(--mut);font-size:12px;margin-top:30px;text-align:center}}
@media(max-width:720px){{.kpis,.grid2{{grid-template-columns:1fr 1fr}}}}
</style></head><body><div class=wrap>
<header>
 <h1>RFM &amp; Dormant-Revenue Reactivation</h1>
 <p>UCI Online Retail · UK e-commerce · {m['date_min']} → {m['date_max']} · {m['orders']:,} orders</p>
</header>

<div class=kpis>
 <div class=kpi><div class=v>{gbp(m['revenue'])}</div><div class=l>Revenue</div></div>
 <div class=kpi><div class=v>{m['customers']:,}</div><div class=l>Customers</div></div>
 <div class=kpi><div class=v>{gbp(m['aov'])}</div><div class=l>Avg Order Value</div></div>
 <div class=kpi hot><div class=v>{gbp(m['react_historical_rev'])}</div><div class=l>Dormant revenue at risk</div></div>
</div>

<div class=card>
 <p class=lead><b>{m['react_customers']} previously-valuable customers</b> have gone quiet for an average of
 <b>{m['react_avg_dormant_days']} days</b>, together representing <b>{gbp(m['react_historical_rev'])}</b> of
 historical revenue. They are not lost — they are <span class=pill>un-called</span>. This is the highest-ROI
 list a sales team can dial: warm, proven buyers who simply stopped.</p>
</div>

<div class=grid2>
 <div class=card><h2>Monthly revenue</h2><img src="{img('monthly_revenue.png')}"></div>
 <div class=card><h2>Revenue by segment</h2><img src="{img('segment_revenue.png')}"></div>
</div>
<div class=card><h2>Dormant ≠ worthless</h2><img src="{img('rfm_scatter.png')}"></div>

<div class=card>
 <h2>RFM segments</h2>
 <table><thead><tr><th>Segment</th><th>Customers</th><th>Revenue</th><th>Avg recency</th><th>Avg orders</th></tr></thead>
 <tbody>{seg_rows}</tbody></table>
</div>

<div class=card>
 <h2>Top reactivation targets — the call list</h2>
 <table><thead><tr><th>Customer</th><th>Country</th><th>Dormant</th><th>Orders</th>
 <th>Lifetime £</th><th>Est. next order</th><th>Priority</th></tr></thead>
 <tbody>{rows}</tbody></table>
 <p style="color:var(--mut);font-size:12px;margin:10px 0 0">Full {m['react_customers']}-row list →
 <code>output/reactivation_targets.csv</code>. Priority = 0.5·monetary + 0.3·frequency + 0.2·recency (percentile-ranked).</p>
</div>

<footer>Built from raw transactions: SQLite + Python (pandas, matplotlib). Extracts in <code>output/extracts/</code> feed Tableau / Power BI.</footer>
</div></body></html>"""
(OUT/"dashboard.html").write_text(html)
print("wrote output/dashboard.html", len(html), "bytes")
