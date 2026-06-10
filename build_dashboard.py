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
:root{{--ink:#16223d;--ink2:#33405c;--acc:#e2574c;--mut:#7c869c;--line:#e7eaef;--bg:#f4f6f9;--card:#fff}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif;
color:var(--ink2);background:var(--bg);-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1060px;margin:0 auto;padding:44px 22px 72px}}
a{{color:var(--acc);text-decoration:none}}
header{{margin-bottom:30px}}
.eyebrow{{color:var(--acc);font-size:12px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;margin:0 0 10px}}
header h1{{font-size:34px;line-height:1.04;letter-spacing:-.025em;font-weight:800;color:var(--ink);margin:0 0 10px;max-width:20ch}}
header p{{color:var(--mut);margin:0;font-size:14px;font-variant-numeric:tabular-nums}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:30px 0}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
.kpi .v{{font-size:25px;font-weight:750;letter-spacing:-.02em;color:var(--ink);font-variant-numeric:tabular-nums}}
.kpi .l{{color:var(--mut);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-top:7px}}
.kpi.hot{{background:var(--ink);border-color:var(--ink)}}.kpi.hot .v{{color:#fff}}.kpi.hot .l{{color:#9fb0c9}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 24px;margin:18px 0}}
.card h2{{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);margin:0 0 18px}}
img{{width:100%;border-radius:8px;display:block}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.lead{{font-size:19px;line-height:1.5;color:var(--ink);max-width:60ch;margin:0;font-weight:450}}
.lead b{{font-weight:700}}.lead .hl{{color:var(--acc);font-weight:700}}
.pill{{display:inline-block;background:#fdecea;color:var(--acc);padding:2px 10px;border-radius:20px;font-size:13px;font-weight:600;white-space:nowrap}}
.tbl{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid #eef1f5;white-space:nowrap}}
td{{font-variant-numeric:tabular-nums}}
th{{color:var(--mut);font-weight:600;text-transform:uppercase;font-size:10.5px;letter-spacing:.04em}}
tbody tr{{transition:background .15s cubic-bezier(.16,1,.3,1)}}
tbody tr:hover{{background:#f8fafc}}
.note{{color:var(--mut);font-size:12px;margin:12px 0 0}}
footer{{color:var(--mut);font-size:12px;margin-top:36px;padding-top:18px;border-top:1px solid var(--line);text-align:center}}
@media(prefers-reduced-motion:no-preference){{
 .rise{{opacity:0;transform:translateY(12px);animation:rise .6s cubic-bezier(.16,1,.3,1) forwards}}
 .kpis .kpi:nth-child(1){{animation-delay:.10s}}.kpis .kpi:nth-child(2){{animation-delay:.17s}}
 .kpis .kpi:nth-child(3){{animation-delay:.24s}}.kpis .kpi:nth-child(4){{animation-delay:.31s}}
 .kpi,.card{{transition:transform .4s cubic-bezier(.16,1,.3,1),box-shadow .4s cubic-bezier(.16,1,.3,1)}}
 .kpi:hover,.card:hover{{transform:translateY(-3px);box-shadow:0 14px 30px -14px rgba(22,34,61,.20)}}
}}
@keyframes rise{{to{{opacity:1;transform:none}}}}
@media(max-width:720px){{
 .wrap{{padding:28px 16px 56px}}
 header h1{{font-size:27px}}
 .kpis{{grid-template-columns:1fr 1fr;gap:10px}}
 .grid2{{grid-template-columns:1fr}}
 .lead{{font-size:17px}}
}}
</style></head><body><div class=wrap>
<header class=rise>
 <p class=eyebrow>Customer Analytics · RFM Segmentation</p>
 <h1>Where the dormant revenue is hiding</h1>
 <p>UCI Online Retail · UK e-commerce · {m['date_min']} to {m['date_max']} · {m['orders']:,} orders analysed</p>
</header>

<div class=kpis>
 <div class="kpi rise"><div class=v>{gbp(m['revenue'])}</div><div class=l>Revenue</div></div>
 <div class="kpi rise"><div class=v>{m['customers']:,}</div><div class=l>Customers</div></div>
 <div class="kpi rise"><div class=v>{gbp(m['aov'])}</div><div class=l>Avg Order Value</div></div>
 <div class="kpi hot rise"><div class=v>{gbp(m['react_historical_rev'])}</div><div class=l>Dormant revenue at risk</div></div>
</div>

<div class=card>
 <p class=lead><b>{m['react_customers']} previously-valuable customers</b> have gone quiet for an average of
 <b>{m['react_avg_dormant_days']} days</b>, together representing <span class=hl>{gbp(m['react_historical_rev'])}</span> of
 historical revenue. They are not lost. They are <span class=pill>un-called</span>: warm, proven buyers who
 simply stopped, and the highest-ROI list a sales team can dial.</p>
</div>

<div class=grid2>
 <div class=card><h2>Monthly revenue</h2><img src="{img('monthly_revenue.png')}"></div>
 <div class=card><h2>Revenue by segment</h2><img src="{img('segment_revenue.png')}"></div>
</div>
<div class=card><h2>Dormant does not mean worthless</h2><img src="{img('rfm_scatter.png')}"></div>

<div class=card>
 <h2>RFM segments</h2>
 <div class=tbl><table><thead><tr><th>Segment</th><th>Customers</th><th>Revenue</th><th>Avg recency</th><th>Avg orders</th></tr></thead>
 <tbody>{seg_rows}</tbody></table></div>
</div>

<div class=card>
 <h2>Top reactivation targets · the call list</h2>
 <div class=tbl><table><thead><tr><th>Customer</th><th>Country</th><th>Dormant</th><th>Orders</th>
 <th>Lifetime £</th><th>Est. next order</th><th>Priority</th></tr></thead>
 <tbody>{rows}</tbody></table></div>
 <p class=note>Full {m['react_customers']}-row list in <code>reactivation_targets.csv</code>.
 Priority = 0.5·monetary + 0.3·frequency + 0.2·recency (percentile-ranked).</p>
</div>

<footer>Built from raw transactions: SQLite + Python (pandas, matplotlib). Extracts feed Tableau / Power BI.</footer>
</div></body></html>"""
(OUT/"dashboard.html").write_text(html)
print("wrote output/dashboard.html", len(html), "bytes")
