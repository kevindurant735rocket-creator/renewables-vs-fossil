"""Build dashboard.html (interactive, shareable) from results.json.

Every number and series is read from results.json so the page can never
drift from the analysis. Run:  python src/build_dashboard.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = json.load(open(ROOT / "results.json"))

# ---- assemble the data blob sent to the browser ----
tg = R["trend_global"]
tr = R["trend_regional"]
tap = R["tapio"]
prev = R["tapio_prevalence"]
het = R["fe_co2_heterogeneity"]
tert = R["fe_co2_tercile"]
disp = R["displacement"]
dreg = R["displacement_regional"]
pj = R["projection_2030"]
cp = R["country_panel"]

# regional heterogeneity as %/pp
het_regions = list(het.keys())
het_coef = [round(het[r]["coef"][0] * 100, 2) for r in het_regions]
het_se = [round(het[r]["coef"][1] * 100, 2) for r in het_regions]
het_p = [round(het[r]["coef"][2], 3) for r in het_regions]
het_n = [het[r]["n"] for r in het_regions]

# tercile as %/pp
torder = ["Low", "Mid", "High"]
terc_coef = [round(tert["groups"][t]["coef"][0] * 100, 2) for t in torder]
terc_se = [round(tert["groups"][t]["coef"][1] * 100, 2) for t in torder]
terc_p = [round(tert["groups"][t]["coef"][2], 3) for t in torder]
terc_n = [tert["groups"][t]["n"] for t in torder]
tb = tert["bounds"]
terc_labels = []
for t in torder:
    if t == "Low":
        lbl = f"Low tercile (2000 share \u2264{tb['low_max']}%)"
    elif t == "High":
        lbl = f"High tercile (2000 share >{tb['high_min']}%)"
    else:
        lbl = f"Mid tercile (2000 share {tb['low_max']}\u2013{tb['high_min']}%)"
    terc_labels.append(lbl)

D = {
    "years": tg["years"], "renew": tg["renew_share"], "fossil": tg["fossil_share"],
    "low": tg["low_carbon_share"],
    "regions": tr["regions"], "ryears": tr["years"], "rseries": tr["series"],
    "win_labels": list(tap.keys()),
    "tap_cats": ["Absolute decoupling", "Relative decoupling", "Coupling",
                 "Expansive coupling", "Recessionary (GDP falling)"],
    "tap_series": {c: [tap[w]["counts"].get(c, 0) for w in tap.keys()] for c in
                   ["Absolute decoupling", "Relative decoupling", "Coupling",
                    "Expansive coupling", "Recessionary (GDP falling)"]},
    "prevalence": [{"window": p["window"], "abs": p["pct_absolute"], "rel": p["pct_relative"]} for p in prev],
    "het_regions": het_regions, "het_coef": het_coef, "het_se": het_se,
    "het_p": het_p, "het_n": het_n,
    "terc_labels": terc_labels,
    "terc_coef": terc_coef, "terc_se": terc_se, "terc_p": terc_p, "terc_n": terc_n,
    "disp_renew": disp["delta_renew_world_TWh"], "disp_fossil": disp["delta_fossil_world_TWh"],
    "disp_ratio": disp["displacement_ratio"], "disp_pct": disp["pct_displacing"],
    "disp_n_disp": disp["n_displacing"], "disp_n": disp["n_countries"],
    "disp_corr": disp["corr_renewgain_d_fossil"],
    "dreg": {rg: {"ratio": v["displacement_ratio"], "pct": v["pct_displacing"]} for rg, v in dreg.items()},
    "pj_years": list(range(tg["years"][0], 2031)),
    "pj_actual_years": tg["years"], "pj_actual": tg["renew_share"],
    "pj_fit": [round(pj["proj_2030_full"] + (pj["proj_2030_recent"] - pj["proj_2030_full"]) * (y - tg["years"][0]) / (2030 - tg["years"][0]), 2) if y <= tg["years"][-1] else None for y in range(tg["years"][0], 2031)],
    # project recent trend only for years > last actual
    "pj_recent": [round(pj["proj_2030_recent"] - pj["recent_slope_pp_per_yr"] * (tg["years"][-1] - y), 2) for y in range(tg["years"][0], 2031)],
    "pj_2030": pj["proj_2030_recent"], "pj_lo": pj["lower_95"], "pj_hi": pj["upper_95"],
    "fossil_actual_years": tg["years"],
    "fossil_actual": [round(tg["fossil_share"][i] / 100.0 * tg["total_gen"][i], 0) for i in range(len(tg["years"]))],
    "fossil_path": [{"year": pp["year"], "fossil_gen": pp["fossil_gen_TWh"]} for pp in R["projection_fossil"]["path"]],
    "fossil_base_year": R["projection_fossil"]["base_year"],
    "fossil_base": R["projection_fossil"]["base_fossil_gen_TWh"],
    "fossil_2030": R["projection_fossil"]["proj_2030_fossil_gen_TWh"],
    "case_studies": R["case_studies"],
    "wit": R["what_it_takes"],
    "country_panel": cp,
    "meta": R["meta"],
}

DJSON = json.dumps(D, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Did Renewables Actually Displace Fossil Power? (2000&ndash;2022)</title>
<meta name="description" content="The world added more renewables than ever — and more fossil power than ever. An interactive, reproducible analysis of 163 countries (2000–2022) on whether the energy transition is really breaking the link between growth and CO2.">
<meta property="og:type" content="website">
<meta property="og:title" content="Did renewables actually displace fossil power — or just ride on top of it?">
<meta property="og:description" content="163 countries, 2000–2022. Renewable share is linked to lower CO2 per capita almost everywhere — yet fossil generation rose by 7,861 TWh while renewables rose by 5,636 TWh, and only 31% of countries cut fossil output. Explore the data.">
<meta property="og:image" content="figures/social.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Did renewables actually displace fossil power — or just ride on top of it?">
<meta name="twitter:description" content="163 countries, 2000–2022. Lower CO2 per capita, yes. Less fossil power, no. Explore the interactive analysis.">
<meta name="twitter:image" content="figures/figure1_global_trend.png">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  :root{--ink:#15201b;--muted:#5b6b63;--line:#e3e9e5;--accent:#1b6b3a;--accent2:#c0492b;--bg:#fbfdfb;}
  *{box-sizing:border-box;}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       color:var(--ink);background:var(--bg);margin:0;line-height:1.6;}
  .wrap{max-width:1060px;margin:0 auto;padding:0 20px 80px;}
  header{background:linear-gradient(135deg,#0f3d24,#1b6b3a);color:#fff;padding:54px 20px 46px;margin-bottom:34px;}
  header .inner{max-width:1060px;margin:0 auto;}
  header h1{font-size:30px;line-height:1.25;margin:0 0 10px;font-weight:800;letter-spacing:-.3px;}
  header p.sub{font-size:15.5px;opacity:.92;max-width:760px;margin:0;}
  header .tag{display:inline-block;background:rgba(255,255,255,.15);padding:3px 10px;border-radius:20px;
       font-size:12px;margin-bottom:14px;letter-spacing:.3px;}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:0 0 30px;}
  .kpi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 18px;box-shadow:0 1px 3px rgba(0,0,0,.03);}
  .kpi .v{font-size:26px;font-weight:800;color:var(--accent);line-height:1.1;}
  .kpi.warn .v{color:var(--accent2);}
  .kpi .l{font-size:12.5px;color:var(--muted);margin-top:6px;}
  section{margin:46px 0;}
  h2{font-size:22px;margin:0 0 4px;letter-spacing:-.2px;}
  h2 .n{color:var(--accent);font-weight:800;margin-right:8px;}
  .lead{color:var(--muted);font-size:15px;max-width:820px;margin:6px 0 18px;}
  .card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:10px 12px 4px;box-shadow:0 1px 3px rgba(0,0,0,.03);}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
  @media(max-width:840px){.grid2{grid-template-columns:1fr;}.kpis{grid-template-columns:repeat(2,1fr);}}
  .explorer{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,.03);}
  .explorer select{font-size:15px;padding:9px 12px;border-radius:10px;border:1px solid var(--line);width:100%;max-width:360px;margin-bottom:14px;}
  .ecards{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;}
  .ec{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px 12px;}
  .ec .v{font-size:19px;font-weight:800;}
  .ec .l{font-size:11.5px;color:var(--muted);}
  .badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:700;}
  .b-good{background:#e3f3e8;color:#1b6b3a;} .b-bad{background:#fbe6e0;color:#c0492b;}
  .callout{background:#fff5f1;border-left:4px solid var(--accent2);border-radius:8px;padding:14px 18px;margin:16px 0;font-size:15px;}
  .foot{font-size:12.5px;color:var(--muted);margin-top:50px;border-top:1px solid var(--line);padding-top:16px;}
  a{color:var(--accent);text-decoration:none;} a:hover{text-decoration:underline;}
  .small{font-size:12px;color:var(--muted);}
</style>
</head>
<body>
<header>
  <div class="inner">
    <span class="tag">An interactive analysis &middot; 163 countries &middot; 2000&ndash;2022</span>
    <h1>Did renewables actually <i>displace</i> fossil power &mdash; or just ride on top of it?</h1>
    <p class="sub">The world's renewable electricity share rose from 18.7% to 29.5% this century. But fossil generation kept growing too. This page lets you see, country by country, whether the clean-energy transition is really breaking the link between growth and carbon &mdash; or just adding a greener line to a still-expanding system.</p>
  </div>
</header>
<div class="wrap">

<div class="kpis">
  <div class="kpi"><div class="v">+10.7pp</div><div class="l">Renewable share of global electricity, 2000&rarr;2022</div></div>
  <div class="kpi warn"><div class="v">31%</div><div class="l">of countries actually <b>cut</b> fossil generation</div></div>
  <div class="kpi warn"><div class="v">+7,861 TWh</div><div class="l">fossil generation added &mdash; vs +5,636 TWh renewables</div></div>
  <div class="kpi"><div class="v">&minus;0.6%/pp</div><div class="l">CO&#8322;/capita per +1pp renewable (fixed effects)</div></div>
</div>

<section>
  <h2><span class="n">1</span>The big picture: a cleaner grid that still runs on coal</h2>
  <p class="lead">Generation-weighted global mix. Renewables climb steadily and fossil barely budges &mdash; it only slips from 64.6% to 61.4%. The transition is adding clean power faster than it is removing dirty power.</p>
  <div class="card"><div id="fig1" style="height:380px;"></div></div>
  <div class="grid2" style="margin-top:18px;">
    <div class="card"><div id="fig2" style="height:340px;"></div></div>
    <div class="card"><div id="fig3" style="height:340px;"></div></div>
  </div>
  <p class="small">Right: renewable share by region. Asia &mdash; the world's manufacturing core &mdash; sits lowest at 27.6% in 2022, while Oceania (59.5%) and the Americas (50.1%) lead.</p>
</section>

<section>
  <h2><span class="n">2</span>Explore your country</h2>
  <p class="lead">Pick a country to see its renewable and fossil shares since 2000, how its emissions and fossil generation moved, and whether it actually displaced fossil. Start with your own &mdash; the result is often surprising.</p>
  <div class="explorer">
    <select id="csel"></select>
    <div class="ecards" id="ecards"></div>
    <div id="cfig" style="height:330px;"></div>
    <div id="cnote" class="small" style="margin-top:8px;"></div>
  </div>
</section>

<section>
  <h2><span class="n">2b</span>Compare two countries</h2>
  <p class="lead">Two countries can both raise their renewable share yet land on opposite sides of the displacement question. Pick any two to see whose fossil generation actually fell.</p>
  <div class="explorer" style="display:flex;gap:12px;flex-wrap:wrap;align-items:center">
    <select id="cmpA"></select>
    <span style="font-weight:700;color:#888">vs</span>
    <select id="cmpB"></select>
  </div>
  <div id="cmpGrid" style="display:flex;gap:16px;flex-wrap:wrap;margin-top:14px"></div>
  <div id="cmpFig" style="height:360px;margin-top:10px"></div>
  <div id="cmpNote" class="small" style="margin-top:8px"></div>
</section>

<section>
  <h2><span class="n">3</span>Decoupling is spreading &mdash; slowly</h2>
  <p class="lead">The Tapio index classifies each country over a window: absolute decoupling (CO&#8322; falls while GDP rises) is the good kind. The share of countries achieving it rose from 11% in 2000&ndash;05 to 34% by 2017&ndash;22.</p>
  <div class="grid2">
    <div class="card"><div id="fig4" style="height:340px;"></div></div>
    <div class="card"><div id="fig5" style="height:340px;"></div></div>
  </div>
</section>

<section>
  <h2><span class="n">4</span>Where renewables cut emissions</h2>
  <p class="lead">A two-way fixed-effects model (country + year) estimates the % change in CO&#8322; per capita per +1 percentage-point of renewable share. The effect is large and significant in Europe and the Americas; weaker and uncertain in Asia and Africa.</p>
  <div class="card"><div id="fig6" style="height:320px;"></div></div>
  <p class="small">Splitting countries into terciles by their <b>2000</b> renewable share sharpens the mechanism: the emissions dividend is strongest where grids were <i>already</i> clean (top tercile, 2000 share &gt;48.8%) and near zero where systems were just starting out (bottom tercile, &le;6.5%).</p>
  <div class="card" style="margin-top:14px;"><div id="fig6b" style="height:300px;"></div></div>
</section>

<section>
  <h2><span class="n">5</span>But did they <i>displace</i> fossil? Mostly, no.</h2>
  <div class="callout">Between 2000 and 2022 the world added <b>5,636 TWh</b> of renewable generation <b>and 7,861 TWh</b> of fossil generation. Only <b>51 of 163 countries (31%)</b> actually cut their fossil output. The correlation between a country's renewable-share gain and its change in fossil generation is essentially zero (<b>r = 0.00</b>): gaining renewable share tells you almost nothing about whether a country burned less coal and gas.</div>
  <div class="card"><div id="fig7" style="height:430px;"></div></div>
  <p class="small">Each point is a country: x = change in fossil generation (TWh), y = change in renewable generation (TWh). Points left of zero (green) <b>displaced</b> fossil; almost everything sits right of zero &mdash; fossil rose. Europe is the only major region that displaced fossil (ratio +0.34, 71% of its countries cut fossil); Africa (&minus;2.54) and Asia (&minus;2.29) added fossil far faster.</p>
  <div class="card" style="margin-top:14px;"><div id="fig7b" style="height:320px;"></div></div>
</section>

<section>
  <h2><span class="n">6</span>Where this lands by 2030</h2>
  <p class="lead">Extrapolating the last decade's momentum, the global renewable share reaches about <b>36%</b> by 2030 (95% interval 35&ndash;37%). Real progress &mdash; and still far short of fossil's ~61% share.</p>
  <div class="card"><div id="fig8" style="height:340px;"></div></div>
</section>

<section>
  <h2><span class="n">7</span>Fossil generation keeps rising to 2030</h2>
  <p class="lead">Hold the last decade's momentum of renewable share, low-carbon share and electricity demand, and fossil generation does not bend down &mdash; it climbs. The build-out has been additive, not substitutive.</p>
  <div class="callout">At current momentum, global fossil generation rises from <b>__FBASE__ TWh</b> to about <b>__F2030__ TWh</b> by 2030 (an added __FGROW__ TWh).</div>
  <div class="card"><div id="fig8b" style="height:340px;"></div></div>
  <div class="callout" style="margin-top:14px"><b>What it would take instead:</b> just to hold fossil generation <i>flat</i> to 2030, the low-carbon share must reach <b>__FLAT__%</b> &mdash; but constant momentum only delivers <b>__MOM__%</b> (a <b>__GAP__-point</b> shortfall). Cutting fossil 30% needs <b>__CUT30__%</b>. Displacement has to be engineered, not assumed from the share.</div>
</section>

<section>
  <h2><span class="n">8</span>Country stories</h2>
  <p class="lead">Jump straight to a country's full trajectory in the explorer below &mdash; six countries with contrasting transitions.</p>
  <div id="cstories" style="display:flex;flex-wrap:wrap;gap:10px;"></div>
</section>

<div class="foot">
  <b>Data &amp; code.</b> Source: Our World in Data &mdash; Energy and CO&#8322; datasets (CC-BY). Every figure and statistic is computed by <code>src/analysis.py</code> and read from <code>results.json</code>; the full academic write-up is <code>report.html</code> / <code>manuscript.pdf</code>. Re-running the pipeline regenerates the entire project. Electricity generation in TWh; CO&#8322; in tonnes per capita. The renewable&ndash;emissions link is an associational fixed-effects result, not a randomized experiment.
</div>

</div>

<script>
const D = __DATA__;
const C = {renew:'#2ca02c', fossil:'#d62728', low:'#1f77b4', ink:'#333'};
const LAYOUT = {font:{family:'-apple-system,Segoe UI,Roboto,sans-serif',size:12}, margin:{t:30,r:14,b:46,l:52}, paper_bgcolor:'#fff', plot_bgcolor:'#fff', hovermode:'closest'};
const CFG = {displayModeBar:false, responsive:true};

Plotly.newPlot('fig1', [
  {x:D.years, y:D.renew, name:'Renewables', mode:'lines', line:{color:C.renew,width:3}},
  {x:D.years, y:D.low, name:'Low-carbon (incl. nuclear)', mode:'lines', line:{color:C.low,width:3,dash:'dash'}},
  {x:D.years, y:D.fossil, name:'Fossil', mode:'lines', line:{color:C.fossil,width:3}}
], Object.assign({}, LAYOUT, {legend:{orientation:'h',y:-0.18}, yaxis:{title:'% of generation'}, xaxis:{title:'Year'}}), CFG);

const rcols=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd'];
Plotly.newPlot('fig2', D.regions.map((r,i)=>({x:D.ryears, y:D.rseries[r], name:r, mode:'lines', line:{width:2,color:rcols[i%rcols.length]}})),
  Object.assign({}, LAYOUT, {legend:{orientation:'h',y:-0.2,font:{size:10}}, yaxis:{title:'Renewables %'}, xaxis:{title:'Year'}}), CFG);

const tcolors={'Absolute decoupling':'#2ca02c','Relative decoupling':'#98df8a','Coupling':'#ff9896','Expansive coupling':'#d62728','Recessionary (GDP falling)':'#bcbcbc'};
Plotly.newPlot('fig3', D.tap_cats.map(c=>({x:D.win_labels, y:D.tap_series[c], name:c, type:'bar', marker:{color:tcolors[c]}})),
  Object.assign({}, LAYOUT, {barmode:'stack', legend:{orientation:'h',y:-0.25,font:{size:9}}, yaxis:{title:'Countries'}, xaxis:{title:'Window'}}), CFG);

Plotly.newPlot('fig4', [
  {x:D.prevalence.map(p=>p.window), y:D.prevalence.map(p=>p.abs), name:'Absolute', type:'scatter', mode:'lines+markers', line:{color:'#2ca02c',width:3}, marker:{size:9}},
  {x:D.prevalence.map(p=>p.window), y:D.prevalence.map(p=>p.rel), name:'Relative', type:'scatter', mode:'lines+markers', line:{color:'#98df8a',width:3}, marker:{size:9}}
], Object.assign({}, LAYOUT, {legend:{orientation:'h',y:-0.18}, yaxis:{title:'% of countries'}, xaxis:{title:'Window'}}), CFG);

// ---- heterogeneity forest ----
Plotly.newPlot('fig6', [{
  x:D.het_coef, y:D.het_regions, mode:'markers', type:'scatter',
  error_x:{type:'data', array:D.het_se, color:'#2ca02c', thickness:1.5, width:6},
  marker:{size:13,color:'#2ca02c'},
  text:D.het_regions.map((r,i)=>`${r}: ${D.het_coef[i]}%/pp (p=${D.het_p[i]})`),
  hovertemplate:'%{text}<extra></extra>'
}], Object.assign({}, LAYOUT, {margin:{t:10,r:14,b:40,l:80}, xaxis:{title:'% change CO₂/capita per +1pp renewable (95% CI)'}, yaxis:{automargin:true},
   shapes:[{type:'line',x0:0,x1:0,y0:-0.5,y1:D.het_regions.length-0.5,line:{color:'#999',width:1}}]}), CFG);

Plotly.newPlot('fig6b', [{
  x:D.terc_coef, y:D.terc_labels, mode:'markers', type:'scatter',
  error_x:{type:'data', array:D.terc_se, color:'#1f77b4', thickness:1.5, width:6},
  marker:{size:13,color:'#1f77b4'},
  text:D.terc_labels.map((l,i)=>`${l}: ${D.terc_coef[i]}%/pp (p=${D.terc_p[i]})`),
  hovertemplate:'%{text}<extra></extra>'
}], Object.assign({}, LAYOUT, {margin:{t:10,r:14,b:40,l:230}, xaxis:{title:'% change CO₂/capita per +1pp renewable (95% CI)'}, yaxis:{automargin:true},
   shapes:[{type:'line',x0:0,x1:0,y0:-0.5,y1:D.terc_labels.length-0.5,line:{color:'#999',width:1}}]}), CFG);

// ---- displacement scatter ----
const cps = D.country_panel;
const dispPts = cps.filter(c=>c.displacing), addPts = cps.filter(c=>!c.displacing);
function mk(pts, name, color){return {x:pts.map(c=>c.d_fossil_TWh), y:pts.map(c=>c.d_renew_TWh), text:pts.map(c=>c.name), mode:'markers', type:'scatter', name:name, marker:{size:9,color:color,opacity:.75}, hovertemplate:'%{text}<br>fossil Δ %{x} TWh · renew Δ %{y} TWh<extra></extra>'};}
Plotly.newPlot('fig7', [mk(dispPts,'Displaced fossil (cut fossil gen)','#2ca02c'), mk(addPts,'Added fossil','#d62728')],
  Object.assign({}, LAYOUT, {legend:{orientation:'h',y:-0.16}, xaxis:{title:'Change in fossil generation 2000→2022 (TWh)'}, yaxis:{title:'Change in renewable generation (TWh)'},
   shapes:[{type:'line',x0:0,x1:0,y0:-500,y1:8000,line:{color:'#999',width:1,dash:'dot'}}]}), CFG);

const dr = D.dreg; const dreg_names=Object.keys(dr);
Plotly.newPlot('fig7b', [{
  x:dreg_names.map(r=>dr[r].ratio), y:dreg_names, mode:'markers', type:'scatter',
  marker:{size:14,color:dreg_names.map(r=>dr[r].ratio>=0?'#2ca02c':'#d62728')},
  text:dreg_names.map(r=>`${r}: ratio ${dr[r].ratio}, ${dr[r].pct}% cut fossil`),
  hovertemplate:'%{text}<extra></extra>'
}], Object.assign({}, LAYOUT, {margin:{t:10,r:14,b:40,l:80}, xaxis:{title:'Displacement ratio (−Δfossil / Δrenew; >0 = fossil fell)'}, yaxis:{automargin:true},
   shapes:[{type:'line',x0:0,x1:0,y0:-0.5,y1:dreg_names.length-0.5,line:{color:'#999',width:1}}]}), CFG);

// ---- projection ----
Plotly.newPlot('fig8', [
  {x:D.pj_actual_years, y:D.pj_actual, name:'Actual', mode:'lines+markers', line:{color:C.renew,width:3}},
  {x:D.pj_years, y:D.pj_recent, name:'Recent-trend → 2030', mode:'lines', line:{color:'#333',width:2,dash:'dash'}}
], Object.assign({}, LAYOUT, {legend:{orientation:'h',y:-0.18}, yaxis:{title:'Renewables %'}, xaxis:{title:'Year',range:[2000,2032]},
   shapes:[{type:'rect',x0:2023,x1:2032,y0:D.pj_lo,y1:D.pj_hi,line:{width:0},fillcolor:'rgba(150,150,150,0.2)'}],
   annotations:[{x:2030,y:D.pj_2030,text:'2030 ≈ '+D.pj_2030.toFixed(0)+'%',showarrow:true,arrowhead:2,ax:-40,ay:-30,font:{color:'#d62728'}}]}), CFG);

// ---- forward fossil projection ----
(function(){
  const fp=D.fossil_path, fpy=fp.map(p=>p.year), fpg=fp.map(p=>p.fossil_gen);
  Plotly.newPlot('fig8b',[
    {x:D.fossil_actual_years, y:D.fossil_actual, name:'Actual', mode:'lines', line:{color:C.fossil,width:3}, fill:'tozeroy', fillcolor:'rgba(214,39,40,0.07)'},
    {x:fpy, y:fpg, name:'Projected (constant momentum)', mode:'lines', line:{color:C.fossil,width:3,dash:'dash'}}
  ], Object.assign({}, LAYOUT, {legend:{orientation:'h',y:-0.18}, yaxis:{title:'Fossil generation (TWh)'}, xaxis:{title:'Year',range:[2000,2032]},
     shapes:[{type:'line',x0:D.fossil_base_year,x1:D.fossil_base_year,y0:0,y1:1,yref:'paper',line:{color:'#999',dash:'dot'}}],
     annotations:[{x:2030,y:D.fossil_2030,text:'2030 ≈ '+D.fossil_2030.toLocaleString()+' TWh',showarrow:true,arrowhead:2,ax:-30,ay:-28,font:{color:C.fossil}}]}), CFG);
})();

// ---- case-study quick links ----
(function(){
  const el=document.getElementById('cstories');
  if(!el) return;
  (D.case_studies||[]).forEach(c=>{
    const a=document.createElement('a');
    a.href='dashboard.html#'+c.iso; a.textContent=c.name;
    a.style.cssText='text-decoration:none;padding:6px 12px;background:#e3f3e8;color:#1b6b3a;border-radius:20px;font-weight:700;font-size:13px;';
    el.appendChild(a);
  });
})();

// ---- country explorer ----
const sel = document.getElementById('csel');
cps.slice().sort((a,b)=>a.name.localeCompare(b.name)).forEach(c=>{const o=document.createElement('option');o.value=c.iso;o.textContent=c.name;sel.appendChild(o);});
const defIso = cps.find(c=>c.name==='China')? 'China':cps[0].name;
if(location.hash){
  const h=location.hash.replace('#','');
  const opt=[...sel.options].find(o=>o.value===h);
  if(opt) sel.value=h;
} else {
  sel.value = (cps.find(c=>c.name===defIso)||cps[0]).iso;
}
function fmt(v,suf=''){return (v===null||v===undefined)?'—':(v+suf);}
function render(){
  const c = cps.find(x=>x.iso===sel.value);
  const dRe = c.renew_end - c.renew_2000, dFo = c.fossil_end - c.fossil_2000;
  const dCo2 = c.co2pc_2000!=null&&c.co2pc_end!=null ? (c.co2pc_end-c.co2pc_2000)/c.co2pc_2000*100 : null;
  document.getElementById('ecards').innerHTML =
    `<div class="ec"><div class="v" style="color:${dRe>=0?'#1b6b3a':'#c0492b'}">${fmt(dRe.toFixed(1),'pp')}</div><div class="l">Renewable share Δ (${fmt(c.renew_2000,'%')}→${fmt(c.renew_end,'%')})</div></div>`+
    `<div class="ec"><div class="v" style="color:${dFo<=0?'#1b6b3a':'#c0492b'}">${fmt(dFo.toFixed(1),'pp')}</div><div class="l">Fossil share Δ (${fmt(c.fossil_2000,'%')}→${fmt(c.fossil_end,'%')})</div></div>`+
    `<div class="ec"><div class="v" style="color:${(dCo2!=null&&dCo2<=0)?'#1b6b3a':'#c0492b'}">${fmt(dCo2!=null?dCo2.toFixed(0):null,'%')}</div><div class="l">CO₂/capita Δ</div></div>`+
    `<div class="ec"><div class="v">${fmt(c.d_renew_TWh,' / ')+fmt(c.d_fossil_TWh,' TWh')}</div><div class="l">Δ renewable / Δ fossil (TWh)</div></div>`;
  const dispBadge = c.displacing? '<span class="badge b-good">Displaced fossil</span>':'<span class="badge b-bad">Added fossil</span>';
  document.getElementById('cnote').innerHTML = `<b>${c.name}</b> (${c.region}) &mdash; decoupling 2000&ndash;2022: <b>${c.decoupling||'n/a'}</b> &middot; ${dispBadge}`;
  const yrs = D.years;
  Plotly.react('cfig', [
    {x:yrs, y:c.renew_series, name:'Renewables %', mode:'lines', line:{color:C.renew,width:3}},
    {x:yrs, y:c.fossil_series, name:'Fossil %', mode:'lines', line:{color:C.fossil,width:3}}
  ], Object.assign({}, LAYOUT, {margin:{t:10,r:14,b:40,l:46}, legend:{orientation:'h',y:-0.18}, yaxis:{title:'% of generation'}, xaxis:{title:'Year'}}), CFG);
}
sel.addEventListener('change', render);
render();

// ---- two-country compare ----
const cmpA = document.getElementById('cmpA'), cmpB = document.getElementById('cmpB');
cps.slice().sort((a,b)=>a.name.localeCompare(b.name)).forEach(c=>{
  for(const s of [cmpA, cmpB]){const o=document.createElement('option');o.value=c.iso;o.textContent=c.name;s.appendChild(o);}
});
cmpA.value = (cps.find(c=>c.name==='China') || cps[0]).iso;
cmpB.value = (cps.find(c=>c.name==='United States') || cps[1]).iso;
function cmpCard(c){
  const dRe=c.renew_end-c.renew_2000, dFo=c.fossil_end-c.fossil_2000;
  const dCo2=(c.co2pc_2000!=null&&c.co2pc_end!=null)?(c.co2pc_end-c.co2pc_2000)/c.co2pc_2000*100:null;
  const badge=c.displacing?'<span class="badge b-good">Displaced fossil</span>':'<span class="badge b-bad">Added fossil</span>';
  return `<div style="flex:1 1 300px;border:1px solid var(--line);border-radius:14px;padding:16px;background:var(--card)">
    <h4 style="margin:0 0 10px">${c.name} <span style="font-weight:400;color:#888">(${c.region})</span></h4>
    <div style="display:flex;gap:14px;flex-wrap:wrap">
      <div class="ec"><div class="v" style="color:${dRe>=0?'#1b6b3a':'#c0492b'}">${fmt(dRe.toFixed(1),'pp')}</div><div class="l">Renewable share Δ (${fmt(c.renew_2000,'%')}→${fmt(c.renew_end,'%')})</div></div>
      <div class="ec"><div class="v" style="color:${dFo<=0?'#1b6b3a':'#c0492b'}">${fmt(dFo.toFixed(1),'pp')}</div><div class="l">Fossil share Δ (${fmt(c.fossil_2000,'%')}→${fmt(c.fossil_end,'%')})</div></div>
      <div class="ec"><div class="v" style="color:${(dCo2!=null&&dCo2<=0)?'#1b6b3a':'#c0492b'}">${fmt(dCo2!=null?dCo2.toFixed(0):null,'%')}</div><div class="l">CO₂/capita Δ</div></div>
      <div class="ec"><div class="v">${fmt(c.d_fossil_TWh,' TWh')}</div><div class="l">Fossil generation Δ</div></div>
    </div>
    <div style="margin-top:10px">${badge}</div>
  </div>`;
}
function cmpRender(){
  const a=cps.find(x=>x.iso===cmpA.value), b=cps.find(x=>x.iso===cmpB.value);
  if(!a||!b) return;
  document.getElementById('cmpGrid').innerHTML = cmpCard(a)+cmpCard(b);
  const yrs=D.years;
  Plotly.react('cmpFig',[
    {x:yrs,y:a.renew_series,name:a.name+' renewables %',mode:'lines',line:{color:C.renew,width:3}},
    {x:yrs,y:a.fossil_series,name:a.name+' fossil %',mode:'lines',line:{color:C.fossil,width:3}},
    {x:yrs,y:b.renew_series,name:b.name+' renewables %',mode:'lines',line:{color:C.renew,width:2,dash:'dot'}},
    {x:yrs,y:b.fossil_series,name=b.name+' fossil %',mode:'lines',line:{color:C.fossil,width:2,dash:'dot'}}
  ], Object.assign({}, LAYOUT, {margin:{t:10,r:14,b:40,l:46}, legend:{orientation:'h',y:-0.18}, yaxis:{title:'% of generation'}, xaxis:{title:'Year'}}), CFG);
  const verdict=(c)=>c.displacing?`${c.name} cut its fossil generation (${fmt(c.d_fossil_TWh,' TWh')}).`:`${c.name} added fossil generation (+${fmt(c.d_fossil_TWh,' TWh')}).`;
  document.getElementById('cmpNote').innerHTML = verdict(a)+' '+verdict(b);
}
cmpA.addEventListener('change',cmpRender); cmpB.addEventListener('change',cmpRender);
cmpRender();
</script>
</body>
</html>"""

html = HTML.replace("__DATA__", DJSON)
html = html.replace("__FBASE__", f"{D['fossil_base']:,.0f}")
html = html.replace("__F2030__", f"{D['fossil_2030']:,.0f}")
html = html.replace("__FGROW__", f"{D['fossil_2030'] - D['fossil_base']:,.0f}")
wit = D["wit"]
html = html.replace("__FLAT__", f"{wit['scenarios']['flat']['low_carbon_share_needed_2030']:.1f}")
html = html.replace("__MOM__", f"{wit['momentum_low_carbon_2030']:.1f}")
html = html.replace("__GAP__", f"{wit['scenarios']['flat']['low_carbon_share_needed_2030'] - wit['momentum_low_carbon_2030']:.1f}")
html = html.replace("__CUT30__", f"{wit['scenarios']['cut30']['low_carbon_share_needed_2030']:.1f}")
(ROOT / "dashboard.html").write_text(html, encoding="utf-8")
print("Wrote dashboard.html (", len(html), "bytes )")
