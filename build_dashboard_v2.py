#!/usr/bin/env python3
"""Interactive product-grade dashboard -> output/dashboard.html (self-contained, ECharts via CDN).
Interactive charts + searchable/sortable reactivation call-list + reactivation-ROI calculator
+ animated signature counter + method note + OG/favicon. Same single-file, same live link."""
import json, csv, pathlib

OUT = pathlib.Path("output")
m = json.load(open(OUT / "metrics.json"))

# segment per customer (join key for real click-to-filter)
seg_by_id = {}
with open(OUT / "extracts/rfm_customers.csv") as f:
    for r in csv.DictReader(f):
        seg_by_id[r["CustomerID"]] = r["segment"]

# reactivation targets -> compact JSON (sorted by priority desc already from analyze.py)
rows = []
with open(OUT / "reactivation_targets.csv") as f:
    for r in csv.DictReader(f):
        rows.append({
            "id": r["CustomerID"],
            "co": r["country"],
            "seg": seg_by_id.get(r["CustomerID"], "?"),
            "rec": int(float(r["recency"])),
            "freq": int(float(r["frequency"])),
            "mon": round(float(r["monetary"])),
            "val": round(float(r["est_reactivation_value"])),
            "score": round(float(r["priority_score"]), 1),
            "last": r["last_purchase"][:10],
        })
rows.sort(key=lambda x: x["score"], reverse=True)

monthly = [l.strip().split(",") for l in open(OUT / "extracts/monthly_revenue.csv")][1:]
monthly = [{"m": r[0], "rev": round(float(r[1]))} for r in monthly]
country = [l.strip().split(",") for l in open(OUT / "extracts/country_revenue.csv")][1:]
country = [{"c": r[0], "rev": round(float(r[1]))} for r in country if r[0] != "United Kingdom"][:8]

seg = m["segments"]
DATA = {"m": m, "rows": rows, "monthly": monthly, "country": country, "seg": seg}

html = """<!doctype html>
<html lang=en>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Customer Reactivation — RFM Analysis | Brian Rodriguez</title>
<meta name=description content="Interactive RFM dashboard on 541K real e-commerce transactions: £1.32M of dormant revenue surfaced as a priority-scored reactivation call list.">
<meta property=og:title content="Customer Reactivation — RFM Analysis">
<meta property=og:description content="£1.32M of dormant revenue, surfaced as a priority-scored call list. Interactive analyst dashboard on 541K real transactions.">
<meta property=og:type content=website>
<meta property=og:url content="https://retail-reactivation.vercel.app">
<meta property=og:image content="https://retail-reactivation.vercel.app/og.png">
<meta property=og:image:width content=1200>
<meta property=og:image:height content=630>
<meta name=twitter:image content="https://retail-reactivation.vercel.app/og.png">
<meta name=twitter:card content=summary_large_image>
<link rel=icon href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%230b1020'/><text y='72' x='50' font-size='62' text-anchor='middle' fill='%234ade80' font-family='Arial' font-weight='bold'>£</text></svg>">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
:root{--bg:#0b1020;--panel:#131a2e;--line:#243049;--ink:#e8edf7;--mut:#8b9bb8;--grn:#4ade80;--amb:#fbbf24;--red:#f87171;--blu:#60a5fa}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding:32px 20px 80px}
.eyebrow{color:var(--grn);font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase}
h1{font-size:34px;font-weight:800;letter-spacing:-.5px;margin:6px 0 4px}
.sub{color:var(--mut);font-size:15px;max-width:640px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0 8px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.kpi .n{font-size:26px;font-weight:800;letter-spacing:-.5px}
.kpi .l{color:var(--mut);font-size:12px;margin-top:3px}
.hero{background:linear-gradient(135deg,#10182e,#0d1424);border:1px solid var(--line);border-radius:18px;padding:34px;margin:26px 0;text-align:center;position:relative;overflow:hidden}
.hero .big{font-size:64px;font-weight:900;letter-spacing:-2px;color:var(--grn);font-variant-numeric:tabular-nums}
.hero .cap{color:var(--mut);font-size:15px;margin-top:6px}
.hero .cap b{color:var(--ink)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:18px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px}
.card h3{font-size:15px;font-weight:700;margin-bottom:2px}
.card .hint{color:var(--mut);font-size:12px;margin-bottom:12px}
.chart{height:280px;width:100%}
.full{grid-column:1/-1}
.roi{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:center}
.roi .out{text-align:center}
.roi .out .v{font-size:46px;font-weight:900;color:var(--grn);letter-spacing:-1px;font-variant-numeric:tabular-nums}
.roi .out .vl{color:var(--mut);font-size:13px;margin-top:2px}
.ctrl{margin:18px 0}
.ctrl label{display:flex;justify-content:space-between;font-size:13px;color:var(--mut);margin-bottom:7px}
.ctrl label b{color:var(--ink);font-size:15px}
input[type=range]{width:100%;accent-color:var(--grn);height:5px}
.tbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
.tbar input{background:#0c1322;border:1px solid var(--line);color:var(--ink);border-radius:9px;padding:9px 12px;font-size:14px;flex:1;min-width:180px}
.tbar .cnt{color:var(--mut);font-size:13px}
.tw{overflow:auto;border:1px solid var(--line);border-radius:12px;max-height:460px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{position:sticky;top:0;background:#0e1526;text-align:left;padding:11px 12px;font-weight:600;color:var(--mut);cursor:pointer;white-space:nowrap;border-bottom:1px solid var(--line);user-select:none}
th:hover{color:var(--ink)}
th.num,td.num{text-align:right;font-variant-numeric:tabular-nums}
td{padding:10px 12px;border-bottom:1px solid #1a2236}
tr:hover td{background:#0e1730}
.pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700}
.method{background:#0c1322;border:1px dashed var(--line);border-radius:14px;padding:18px 22px;margin-top:24px;color:var(--mut);font-size:13px;line-height:1.7}
.method b{color:var(--ink)}
.foot{margin-top:34px;color:var(--mut);font-size:13px;display:flex;gap:18px;flex-wrap:wrap}
.foot a{color:var(--blu);text-decoration:none}
@media(max-width:760px){.kpis,.grid2,.roi{grid-template-columns:1fr}.hero .big{font-size:44px}h1{font-size:26px}}
</style>
</head>
<body>
<div class=wrap>
  <div class=eyebrow>RFM Segmentation · Real UK E-commerce · 541K transactions</div>
  <h1>Customer Reactivation Dashboard</h1>
  <p class=sub>Where is the dormant revenue, who do we call first, and what's it worth? Built end-to-end: raw data → SQL warehouse → RFM model → priority-scored call list.</p>

  <div class=kpis>
    <div class=kpi><div class=n>£__REV__M</div><div class=l>Total revenue analyzed</div></div>
    <div class=kpi><div class=n>__CUST__</div><div class=l>Customers</div></div>
    <div class=kpi><div class=n>£__AOV__</div><div class=l>Avg order value</div></div>
    <div class=kpi><div class=n>__TOP10__%</div><div class=l>Revenue from top 10% of customers</div></div>
  </div>

  <div class=hero>
    <div class=big id=counter>£0</div>
    <div class=cap><b>__REACT__ previously-valuable customers</b> have gone quiet (avg __DORM__ days). That's historical revenue sitting idle — recoverable.</div>
  </div>

  <div class=grid2>
    <div class=card><h3>Revenue by customer segment</h3><div class=hint>Click a bar to filter the call list ↓</div><div id=segChart class=chart></div></div>
    <div class=card><h3>Monthly revenue trend</h3><div class=hint>Q4 ramp — reactivate before the peak, not during</div><div id=monChart class=chart></div></div>
  </div>

  <div class="card full">
    <h3>Reactivation ROI calculator</h3><div class=hint>Drag to model a campaign. Math runs on the real priority-ranked customers below.</div>
    <div class=roi>
      <div>
        <div class=ctrl><label><span>Customers to dial (top by priority)</span><b id=dialN>100</b></label><input type=range id=dial min=10 max=__NREACT__ value=100 step=10></div>
        <div class=ctrl><label><span>Assumed reactivation rate</span><b id=rateN>20%</b></label><input type=range id=rate min=5 max=40 value=20 step=1></div>
        <div class=hint id=roiBasis></div>
      </div>
      <div class=out><div class=v id=roiVal>£0</div><div class=vl>projected recovered revenue</div></div>
    </div>
  </div>

  <div class=grid2>
    <div class=card><h3>Top export markets (ex-UK)</h3><div class=hint>Where overseas revenue concentrates</div><div id=ctyChart class=chart></div></div>
    <div class=card><h3>Segment health</h3><div class=hint>Recency vs spend — bubble size = customer count</div><div id=bubChart class=chart></div></div>
  </div>

  <div class="card full">
    <h3>Priority reactivation call list</h3><div class=hint>The deliverable — sortable, searchable. Score = 0.5·spend + 0.3·frequency + 0.2·recency.</div>
    <div class=tbar>
      <input id=q placeholder="Search by customer ID or country…">
      <span class=pill id=segFilter style="display:none;cursor:pointer;background:#fbbf2422;color:#fbbf24"></span>
      <span class=cnt id=tcnt></span>
    </div>
    <div class=tw><table id=tbl><thead><tr>
      <th data-k=score class=num>Priority ▾</th><th data-k=id>Customer</th><th data-k=seg>Segment</th><th data-k=co>Country</th>
      <th data-k=rec class=num>Days quiet</th><th data-k=freq class=num>Orders</th>
      <th data-k=mon class=num>Lifetime £</th><th data-k=val class=num>Reactiv. value £</th><th data-k=last>Last order</th>
    </tr></thead><tbody id=tbody></tbody></table></div>
  </div>

  <div class=method>
    <b>Method &amp; caveats.</b> Source: UCI Online Retail (Chen, 2015) — a real UK gift retailer, 1 Dec 2010 – 9 Dec 2011, 541,909 line items.
    Cancellations (credit invoices) and non-positive quantity/price rows excluded → 397,884 clean sales lines.
    RFM scored per customer; "dormancy" = recency &gt; ~90 days against the 9 Dec 2011 snapshot. Reactivation value is a conservative estimate
    (historical spend × a damped probability), not a guarantee. ROI calculator applies your chosen rate to the real lifetime spend of the top-N priority customers.
    Currency = GBP as in source. Fully reproducible — see GitHub.
  </div>

  <div class=foot>
    <span>Brian Rodriguez · Data Analyst</span>
    <a href="https://github.com/00BROD/rfm-reactivation-portfolio">GitHub repo →</a>
    <a href="https://insightflow-navy.vercel.app">InsightFlow (another build) →</a>
  </div>
</div>

<script>
const D=__DATA__;
const f0=n=>'£'+Math.round(n).toLocaleString();
const fk=n=>n>=1e6?'£'+(n/1e6).toFixed(2)+'M':n>=1e3?'£'+Math.round(n/1e3)+'k':'£'+Math.round(n);
const segColor={'Champions':'#4ade80','Loyal':'#60a5fa','At Risk (was valuable)':'#fbbf24','Recent / New':'#a78bfa','Lapsed / Low':'#64748b'};
const axis={axisLine:{lineStyle:{color:'#243049'}},axisLabel:{color:'#8b9bb8'},splitLine:{lineStyle:{color:'#1a2236'}}};
const tip={backgroundColor:'#131a2e',borderColor:'#243049',textStyle:{color:'#e8edf7'}};

// signature counter
(()=>{const el=document.getElementById('counter'),T=D.m.react_historical_rev,t0=performance.now(),dur=1600;
function step(t){let p=Math.min((t-t0)/dur,1);p=1-Math.pow(1-p,3);el.textContent=f0(T*p);if(p<1)requestAnimationFrame(step)}
const io=new IntersectionObserver(e=>{if(e[0].isIntersecting){requestAnimationFrame(step);io.disconnect()}});io.observe(el);})();

// segment bar (click to filter)
const segData=[...D.seg].sort((a,b)=>b.revenue-a.revenue);
const segC=echarts.init(document.getElementById('segChart'),'dark');
segC.setOption({backgroundColor:'',grid:{left:8,right:24,top:16,bottom:8,containLabel:true},tooltip:{...tip,formatter:p=>`${p.name}<br><b>${f0(p.value)}</b> · ${segData[p.dataIndex].customers} customers`},
xAxis:{type:'value',...axis,axisLabel:{...axis.axisLabel,formatter:v=>fk(v)}},
yAxis:{type:'category',data:segData.map(s=>s.segment),...axis},
series:[{type:'bar',data:segData.map(s=>({value:s.revenue,itemStyle:{color:segColor[s.segment]||'#60a5fa',borderRadius:[0,5,5,0]}})),barWidth:'58%'}]});
segC.on('click',p=>{setSegFilter(segFilterVal===p.name?null:p.name);
document.getElementById('tbl').scrollIntoView({behavior:'smooth',block:'center'})});

// monthly line
const monC=echarts.init(document.getElementById('monChart'),'dark');
monC.setOption({backgroundColor:'',grid:{left:8,right:18,top:18,bottom:8,containLabel:true},tooltip:{trigger:'axis',...tip,formatter:p=>`${p[0].name}<br><b>${f0(p[0].value)}</b>`},
xAxis:{type:'category',data:D.monthly.map(r=>r.m.slice(2)),...axis,axisLabel:{...axis.axisLabel,rotate:45,fontSize:10}},
yAxis:{type:'value',...axis,axisLabel:{...axis.axisLabel,formatter:v=>fk(v)}},
series:[{type:'line',smooth:true,data:D.monthly.map(r=>r.rev),lineStyle:{color:'#4ade80',width:3},itemStyle:{color:'#4ade80'},areaStyle:{color:'rgba(74,222,128,.12)'}}]});

// country bar
const ctyC=echarts.init(document.getElementById('ctyChart'),'dark');
ctyC.setOption({backgroundColor:'',grid:{left:8,right:24,top:16,bottom:8,containLabel:true},tooltip:{...tip,formatter:p=>`${p.name}<br><b>${f0(p.value)}</b>`},
xAxis:{type:'value',...axis,axisLabel:{...axis.axisLabel,formatter:v=>fk(v)}},
yAxis:{type:'category',data:D.country.map(c=>c.c).reverse(),...axis},
series:[{type:'bar',data:D.country.map(c=>c.rev).reverse(),itemStyle:{color:'#60a5fa',borderRadius:[0,5,5,0]},barWidth:'58%'}]});

// segment bubble: recency vs orders, size=customers
const bubC=echarts.init(document.getElementById('bubChart'),'dark');
bubC.setOption({backgroundColor:'',grid:{left:8,right:24,top:20,bottom:30,containLabel:true},
tooltip:{...tip,formatter:p=>`${p.data[3]}<br>recency <b>${p.data[0]}d</b> · ${p.data[1]} avg orders · ${p.data[2]} cust`},
xAxis:{type:'value',name:'Avg days since order',nameTextStyle:{color:'#8b9bb8'},nameLocation:'middle',nameGap:26,...axis},
yAxis:{type:'value',name:'Avg orders',nameTextStyle:{color:'#8b9bb8'},...axis},
series:[{type:'scatter',data:D.seg.map(s=>[Math.round(s.avg_recency),s.avg_orders,s.customers,s.segment]),
symbolSize:d=>Math.max(14,Math.sqrt(d[2])*2.4),itemStyle:{color:p=>segColor[p.data[3]]||'#60a5fa',opacity:.85}}]});

addEventListener('resize',()=>[segC,monC,ctyC,bubC].forEach(c=>c.resize()));

// ROI calculator — runs on real priority-sorted lifetime spend
const R=D.rows,cum=[];let s=0;for(const r of R){s+=r.mon;cum.push(s)}
const dial=document.getElementById('dial'),rate=document.getElementById('rate');
function roi(){const n=+dial.value,pr=+rate.value;document.getElementById('dialN').textContent=n;document.getElementById('rateN').textContent=pr+'%';
const base=cum[Math.min(n,cum.length)-1];const out=base*pr/100;
document.getElementById('roiVal').textContent=f0(out);
document.getElementById('roiBasis').textContent=`Top ${n} customers = ${f0(base)} lifetime spend. At ${pr}% reactivation → ${f0(out)} recovered.`;}
dial.oninput=rate.oninput=roi;roi();

// call list table — search + segment filter (driven by chart clicks) + sort
let sortK='score',sortDir=-1,query='',segFilterVal=null;
const tbody=document.getElementById('tbody'),tcnt=document.getElementById('tcnt'),segFEl=document.getElementById('segFilter');
const inList=new Set(R.map(x=>x.seg));
function pill(sc){const c=sc>=70?'#4ade80':sc>=40?'#fbbf24':'#64748b';return `<span class=pill style="background:${c}22;color:${c}">${sc}</span>`}
function segPill(s){const c=segColor[s]||'#64748b';return `<span class=pill style="background:${c}22;color:${c}">${s.replace(' (was valuable)','')}</span>`}
function setSegFilter(s){segFilterVal=s;
if(s){segFEl.style.display='inline-block';segFEl.textContent=(inList.has(s)?'✕ ':'')+s;
const c=segColor[s]||'#64748b';segFEl.style.background=c+'22';segFEl.style.color=c;}
else segFEl.style.display='none';
render();}
segFEl.onclick=()=>setSegFilter(null);
function render(){let r=R.filter(x=>(!query||x.id.includes(query)||x.co.toLowerCase().includes(query))&&(!segFilterVal||x.seg===segFilterVal));
r=r.sort((a,b)=>(a[sortK]>b[sortK]?1:a[sortK]<b[sortK]?-1:0)*sortDir);
tcnt.textContent=segFilterVal&&!inList.has(segFilterVal)
  ?`0 of ${R.length} — "${segFilterVal}" customers are healthy, not on the call list`
  :`${r.length} of ${R.length} customers`;
tbody.innerHTML=r.slice(0,300).map(x=>`<tr><td class=num>${pill(x.score)}</td><td>#${x.id}</td><td>${segPill(x.seg)}</td><td>${x.co}</td><td class=num>${x.rec}</td><td class=num>${x.freq}</td><td class=num>£${x.mon.toLocaleString()}</td><td class=num>£${x.val.toLocaleString()}</td><td>${x.last}</td></tr>`).join('');}
document.querySelectorAll('th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(k===sortK)sortDir*=-1;else{sortK=k;sortDir=(k==='id'||k==='co'||k==='last'||k==='seg')?1:-1}
document.querySelectorAll('th').forEach(t=>t.textContent=t.textContent.replace(/ [▾▴]/,''));th.textContent+=sortDir<0?' ▾':' ▴';render()});
document.getElementById('q').oninput=e=>{query=e.target.value.toLowerCase().trim();render()};
render();
</script>
</body></html>"""

html = (html
    .replace("__DATA__", json.dumps(DATA, separators=(",", ":")))
    .replace("__REV__", f"{m['revenue']/1e6:.1f}")
    .replace("__CUST__", f"{m['customers']:,}")
    .replace("__AOV__", f"{m['aov']:.0f}")
    .replace("__TOP10__", str(m["top10_pct_rev"]))
    .replace("__REACT__", f"{m['react_customers']:,}")
    .replace("__DORM__", str(m["react_avg_dormant_days"]))
    .replace("__NREACT__", str(len(rows))))

(OUT / "dashboard.html").write_text(html)
print(f"wrote output/dashboard.html  {len(html)//1024}KB  ({len(rows)} call-list rows embedded)")
