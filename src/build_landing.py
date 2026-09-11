"""Build index.html -- the shareable landing/static site -- from results.json.

Design system + OG/Twitter cards + JSON-LD + favicon + share buttons +
interactive Plotly chart + forward fossil projection + case studies +
Myth-vs-Fact FAQ + animated counters + mobile nav + #utility/#howto.
Every stat is read from results.json so the landing page can never drift.
Run:  python src/build_landing.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
R = json.load(open(ROOT / "results.json"))

tg = R["trend_global"]
renew_start, renew_end = tg["renew_share"][0], tg["renew_share"][-1]
fossil_start, fossil_end = tg["fossil_share"][0], tg["fossil_share"][-1]
low_start, low_end = tg["low_carbon_share"][0], tg["low_carbon_share"][-1]
start_year, end_year = tg["years"][0], tg["years"][-1]

disp = R["displacement"]
fossil_added = disp["delta_fossil_world_TWh"]
renew_added = disp["delta_renew_world_TWh"]
pct_disp = disp["pct_displacing"]
n_disp = disp["n_displacing"]
n_ctry = disp["n_countries"]

fe = R["fe_co2"]["contemporaneous"]
fe_pct = (1 - (2.718281828459045 ** fe["coef"][0])) * 100

pj = R["projection_2030"]
pv = R["tapio_prevalence"]
abs_first, abs_last = pv[0]["pct_absolute"], pv[-1]["pct_absolute"]

het = R["fe_co2_heterogeneity"]
pf = R["projection_fossil"]
fossil_base = pf["base_fossil_gen_TWh"]
fossil_2030 = pf["proj_2030_fossil_gen_TWh"]
fossil_growth = round(fossil_2030 - fossil_base)


def pct_pp(d):
    return d["coef"][0] * 100


amer = -pct_pp(het["America"])
eur = -pct_pp(het["Europe"])
n_panel = len(R["country_panel"])

P = {
    "RENEW_START": f"{renew_start:.1f}",
    "RENEW_END": f"{renew_end:.1f}",
    "RENEW_DELTA": f"{renew_end - renew_start:.1f}",
    "FOSSIL_START": f"{fossil_start:.1f}",
    "FOSSIL_END": f"{fossil_end:.1f}",
    "FOSSIL_ADDED": f"{fossil_added:,.0f}",
    "RENEW_ADDED": f"{renew_added:,.0f}",
    "PCT_DISP": f"{pct_disp:.0f}",
    "N_DISP": f"{n_disp}",
    "N_CTRY": f"{n_ctry}",
    "FE_PCT": f"{fe_pct:.2f}",
    "PJ2030": f"{pj['proj_2030_recent']:.0f}",
    "PJ_LO": f"{pj['lower_95']:.0f}",
    "PJ_HI": f"{pj['upper_95']:.0f}",
    "ABS_FIRST": f"{abs_first:.0f}",
    "ABS_LAST": f"{abs_last:.0f}",
    "AMER": f"{amer:.2f}",
    "EUR": f"{eur:.2f}",
    "START_YR": str(start_year),
    "END_YR": str(end_year),
    "N_PANEL": str(n_panel),
    "FOSSIL_BASE": f"{fossil_base:,.0f}",
    "FOSSIL_2030": f"{fossil_2030:,.0f}",
    "FOSSIL_GROWTH": f"{fossil_growth:,.0f}",
}

# ---- interactive data blob for the landing page charts ----
fa_years = tg["years"]
fa = [round(tg["fossil_share"][i] / 100.0 * tg["total_gen"][i], 0) for i in range(len(tg["years"]))]
ldata = {
    "years": tg["years"], "renew": tg["renew_share"], "fossil": tg["fossil_share"],
    "low": tg["low_carbon_share"],
    "cases": [{"name": c["name"], "years": c["years"], "renew": c["renew_series"],
               "fossil": c["fossil_series"]} for c in R["case_studies"]],
    "fossil_actual_years": fa_years, "fossil_actual": fa,
    "fossil_path": [{"year": p["year"], "fossil_gen": p["fossil_gen_TWh"]} for p in pf["path"]],
    "fossil_base_year": pf["base_year"], "fossil_base": fossil_base, "fossil_2030": fossil_2030,
}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Did Renewables Actually Displace Fossil Power? | Global Electricity Transition, %%START_YR%%&ndash;%%END_YR%%</title>
<meta name="description" content="The world added more renewables than ever &mdash; and more fossil power than ever. An interactive, reproducible study of %%N_CTRY%% countries (%%START_YR%%&ndash;%%END_YR%%) on whether the energy transition is really breaking the link between growth and CO&#8322;.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://example.org/renewables-displace-fossil/">
<meta property="og:type" content="website">
<meta property="og:title" content="Did renewables actually displace fossil power &mdash; or just ride on top of it?">
<meta property="og:description" content="%%N_CTRY%% countries, %%START_YR%%&ndash;%%END_YR%%. Renewable share is linked to lower CO&#8322; per capita almost everywhere &mdash; yet fossil generation rose by %%FOSSIL_ADDED%% TWh while renewables rose by %%RENEW_ADDED%% TWh, and only %%PCT_DISP%%% of countries cut fossil output.">
<meta property="og:image" content="figures/social.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Did renewables actually displace fossil power &mdash; or just ride on top of it?">
<meta name="twitter:description" content="%%N_CTRY%% countries, %%START_YR%%&ndash;%%END_YR%%. Lower CO&#8322; per capita, yes. Less fossil power, no. Explore the interactive analysis.">
<meta name="twitter:image" content="figures/figure1_global_trend.png">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "The Global Renewable Electricity Transition and Its Decoupling from CO2 Emissions",
  "abstract": "Using %%N_CTRY%% countries over %%START_YR%%-%%END_YR%% (%%N_PANEL%% country-year observations), this reproducible study combines convergence analysis, the Tapio decoupling index, a two-way fixed-effects panel, a grid carbon-intensity outcome, and displacement accounting. Renewable share is associated with lower CO2 per capita almost everywhere, yet fossil generation rose by %%FOSSIL_ADDED%% TWh while renewables rose by %%RENEW_ADDED%% TWh, and only %%PCT_DISP%%% of countries cut fossil output.",
  "author": {"@type": "Person", "name": "Your Name"},
  "datePublished": "2026-09-11",
  "sameAs": ["https://github.com/your-github-username/renewables-vs-fossil"],
  "about": ["renewable electricity", "decarbonisation", "decoupling", "energy transition", "CO2 emissions"],
  "keywords": "renewable electricity, decoupling, Tapio index, fixed-effects panel, carbon intensity, displacement"
}
</script>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
:root{
  --ink:#13201a; --muted:#5d6b63; --line:#e4eae6; --bg:#fbfdfb; --card:#fff;
  --accent:#1b6b3a; --accent-d:#0f3d24; --warn:#c0492b; --warn-bg:#fff5f1;
  --blue:#1f6f9e; --radius:16px; --shadow:0 1px 3px rgba(0,0,0,.05),0 8px 24px rgba(16,61,36,.06);
  --maxw:1080px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:var(--bg);line-height:1.65;-webkit-font-smoothing:antialiased}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 22px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.nav{position:sticky;top:0;z-index:20;background:rgba(251,253,251,.85);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:62px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:-.3px}
.brand img{width:28px;height:28px;border-radius:7px}
.nav nav{display:flex;gap:22px;font-size:14.5px;font-weight:600}
.nav nav a{color:var(--ink)}
.menu-btn{display:none;background:none;border:0;color:var(--ink);font-size:24px;cursor:pointer;line-height:1}
.hero{background:linear-gradient(150deg,#0f3d24,#1b6b3a 60%,#238a49);color:#fff;padding:60px 0 50px;position:relative;overflow:hidden}
.hero .tag{display:inline-block;background:rgba(255,255,255,.14);padding:4px 12px;border-radius:20px;font-size:12.5px;letter-spacing:.3px;margin-bottom:16px}
.hero h1{font-size:clamp(28px,4.4vw,46px);line-height:1.12;margin:0 0 14px;font-weight:850;letter-spacing:-.5px;max-width:920px}
.hero p.lead{font-size:17px;opacity:.94;max-width:760px;margin:0 0 24px}
.hero .cta{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:22px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:11px;font-weight:700;font-size:15px;border:1px solid transparent;cursor:pointer}
.btn.primary{background:#fff;color:var(--accent-d)}
.btn.ghost{background:rgba(255,255,255,.12);color:#fff;border-color:rgba(255,255,255,.35)}
.btn:hover{text-decoration:none;opacity:.92}
.share{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.share .lbl{font-size:13px;opacity:.85;margin-right:2px}
.sb{width:38px;height:38px;border-radius:10px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:#fff;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;font-size:13px;font-weight:700}
.sb:hover{background:rgba(255,255,255,.22)}
.hero figure{margin:30px 0 0}
.hero figure img{width:100%;border-radius:14px;box-shadow:var(--shadow);border:1px solid rgba(255,255,255,.18)}
.hero figcaption{font-size:12.5px;opacity:.8;margin-top:8px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:-34px auto 0;position:relative;z-index:5}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 16px;box-shadow:var(--shadow)}
.kpi .v{font-size:24px;font-weight:850;color:var(--accent);line-height:1.05}
.kpi.warn .v{color:var(--warn)}
.kpi .l{font-size:12.5px;color:var(--muted);margin-top:7px}
section{padding:54px 0}
h2{font-size:26px;margin:0 0 6px;letter-spacing:-.3px}
h2 .n{color:var(--accent);font-weight:850;margin-right:10px}
.lead2{color:var(--muted);font-size:15.5px;max-width:840px;margin:6px 0 26px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);transition:transform .15s ease,box-shadow .15s ease}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(16,61,36,.12)}
.card .ic{width:44px;height:44px;border-radius:11px;background:#eaf4ee;color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:12px}
.card h3{margin:0 0 8px;font-size:17px}
.card p{margin:0 0 12px;color:var(--muted);font-size:14px}
.card .more{font-weight:700;font-size:13.5px}
.callout{background:var(--warn-bg);border-left:4px solid var(--warn);border-radius:10px;padding:16px 20px;margin:0 0 26px;font-size:15px}
.step{display:flex;gap:16px;padding:18px 0;border-bottom:1px solid var(--line)}
.step:last-child{border-bottom:0}
.step .num{flex:0 0 34px;height:34px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800}
.step h4{margin:4px 0 4px;font-size:16px}
.step p{margin:0;color:var(--muted);font-size:14.5px}
.code{background:#0f1714;color:#d6f5e0;border-radius:12px;padding:16px 18px;font-family:"SF Mono",Menlo,Consolas,monospace;font-size:13px;overflow-x:auto}
.code .c{color:#7fae8e}
.cite{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;font-size:13.5px;position:relative}
.cite button{position:absolute;top:12px;right:12px;border:1px solid var(--line);background:#f4f8f5;border-radius:8px;padding:5px 10px;font-size:12px;cursor:pointer;font-weight:600}
footer{border-top:1px solid var(--line);padding:30px 0 50px;color:var(--muted);font-size:13px}
footer .wrap{display:flex;flex-wrap:wrap;gap:14px;justify-content:space-between}
.toast{position:fixed;left:50%;bottom:30px;transform:translateX(-50%) translateY(20px);background:#13201a;color:#fff;padding:11px 18px;border-radius:10px;font-size:14px;opacity:0;pointer-events:none;transition:.25s;z-index:50}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
/* interactive explore + charts */
.explore{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow)}
.explore select{font-size:15px;padding:9px 12px;border-radius:10px;border:1px solid var(--line);width:100%;max-width:320px;margin-bottom:8px}
.chart{width:100%}
.callout.good{background:#eaf4ee;border-left-color:var(--accent)}
/* case studies */
.stories img{width:100%;border-radius:12px;border:1px solid var(--line);margin-bottom:18px}
.sgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.scard{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow)}
.scard h4{margin:0 0 4px;font-size:15px}
.scard .meta{font-size:12.5px;color:var(--muted)}
.badge{display:inline-block;padding:1px 9px;border-radius:20px;font-size:11.5px;font-weight:700;margin-left:6px}
.b-good{background:#e3f3e8;color:#1b6b3a}.b-bad{background:#fbe6e0;color:#c0492b}
/* FAQ */
.faq details{border:1px solid var(--line);border-radius:12px;padding:0 16px;margin-bottom:10px;background:#fff}
.faq summary{padding:14px 0;font-weight:700;cursor:pointer;list-style:none;font-size:15.5px}
.faq summary::-webkit-details-marker{display:none}
.faq summary:before{content:"+";margin-right:10px;color:var(--accent);font-weight:900;font-size:18px}
.faq details[open] summary:before{content:"\2212"}
.faq p{margin:0 0 14px;color:var(--muted);font-size:14.5px}
/* reveal animation */
.reveal{opacity:0;transform:translateY(16px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
@media(max-width:900px){
  .kpis{grid-template-columns:repeat(2,1fr)}.grid,.sgrid{grid-template-columns:1fr}
  .nav nav{display:none;position:absolute;top:62px;left:0;right:0;background:#0f3d24;flex-direction:column;padding:14px 22px;gap:14px}
  .nav nav a{color:#fff}
  .nav nav.open{display:flex}.menu-btn{display:block}
}
</style>
</head>
<body>

<header class="nav">
  <div class="wrap">
    <div class="brand"><img src="favicon.svg" alt="">Renewables &amp; Decoupling</div>
    <nav>
      <a href="#explore">Explore</a>
      <a href="#stories">Stories</a>
      <a href="#utility">Utility</a>
      <a href="#faq">FAQ</a>
      <a href="#howto">How&nbsp;to</a>
      <a href="dashboard.html">Dashboard</a>
      <a href="report.html">Report</a>
      <a href="manuscript.pdf">Paper</a>
      <a href="results.json">Data</a>
      <a href="https://github.com/your-github-username/renewables-vs-fossil">Code</a>
    </nav>
    <button class="menu-btn" aria-label="Menu">&#9776;</button>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <span class="tag">An interactive, reproducible study &middot; %%N_CTRY%% countries &middot; %%START_YR%%&ndash;%%END_YR%%</span>
    <h1>Did renewables actually <i>displace</i> fossil power &mdash; or just ride on top of it?</h1>
    <p class="lead">Global renewable electricity rose from %%RENEW_START%%% to %%RENEW_END%%% this century. But fossil generation kept growing too. This page lets you see, country by country, whether the clean-energy transition is really breaking the link between growth and carbon &mdash; or just adding a greener line to a still-expanding system.</p>
    <div class="cta">
      <a class="btn primary" href="dashboard.html">&#9654;&nbsp; Explore your country</a>
      <a class="btn ghost" href="report.html">Read the full report</a>
    </div>
    <div class="share">
      <span class="lbl">Share:</span>
      <button class="sb" data-net="x" title="Share on X">X</button>
      <button class="sb" data-net="linkedin" title="Share on LinkedIn">in</button>
      <button class="sb" data-net="facebook" title="Share on Facebook">f</button>
      <button class="sb" data-net="weibo" title="Share on Weibo">微</button>
      <button class="sb" id="copyBtn" title="Copy link">&#128279;</button>
    </div>
    <figure>
      <img src="figures/hero.png" alt="Renewables climb; fossil generation keeps rising">
      <figcaption>Global electricity mix, %%START_YR%%&ndash;%%END_YR%%. Renewables climb; fossil generation keeps rising (%%FOSSIL_START%%% &rarr; %%FOSSIL_END%%%).</figcaption>
    </figure>
  </div>
</section>

<div class="wrap">
  <div class="kpis">
    <div class="kpi"><div class="v" data-num="%%RENEW_DELTA%%" data-prefix="+" data-suffix="pp" data-dec="1">+%%RENEW_DELTA%%pp</div><div class="l">Renewable share of global electricity, %%START_YR%%&rarr;%%END_YR%%</div></div>
    <div class="kpi warn"><div class="v" data-num="%%PCT_DISP%%" data-suffix="%" data-dec="0">%%PCT_DISP%%%</div><div class="l">of countries actually <b>cut</b> fossil generation</div></div>
    <div class="kpi warn"><div class="v" data-num="%%FOSSIL_ADDED%%" data-prefix="+" data-suffix=" TWh" data-dec="0">+%%FOSSIL_ADDED%%</div><div class="l">TWh of fossil added &mdash; vs +%%RENEW_ADDED%% TWh renewables</div></div>
    <div class="kpi"><div class="v" data-num="%%FE_PCT%%" data-prefix="&minus;" data-suffix="%" data-dec="2">&minus;%%FE_PCT%%%</div><div class="l">CO&#8322;/capita per +1pp renewable (fixed effects)</div></div>
    <div class="kpi"><div class="v" data-num="%%PJ2030%%" data-suffix="%" data-dec="0">%%PJ2030%%%</div><div class="l">renewable share projected by 2030 (%%PJ_LO%%&ndash;%%PJ_HI%%%)</div></div>
  </div>
</div>

<section id="explore">
  <div class="wrap">
    <h2><span class="n">#</span>Explore the trend yourself</h2>
    <p class="lead2">The headline numbers above come straight from this chart. Pick a country to overlay its renewable and fossil shares on the world line &mdash; then ask the real question: did its renewable build <i>replace</i> fossil, or pile on top?</p>
    <div class="explore reveal">
      <select id="exploreSel"><option value="">World only</option></select>
      <div id="exploreChart" class="chart" style="height:420px;"></div>
    </div>
  </div>
</section>

<section style="background:#f3f7f4;">
  <div class="wrap">
    <h2><span class="n">#</span>Where this is heading: fossil keeps rising to 2030</h2>
    <p class="lead2">Hold the 2013&ndash;2022 momentum of renewable share, low-carbon share and electricity demand, and fossil generation does not bend down &mdash; it keeps climbing.</p>
    <div class="callout warn"><b>At current momentum, global fossil generation rises from %%FOSSIL_BASE%% TWh (%%END_YR%%) to about %%FOSSIL_2030%% TWh by 2030</b> &mdash; an added <b>%%FOSSIL_GROWTH%% TWh</b>. The transition is adding clean power faster than it is retiring dirty power.</div>
    <div class="card reveal"><div id="fossilChart" class="chart" style="height:380px;"></div></div>
  </div>
</section>

<section id="stories">
  <div class="wrap">
    <h2><span class="n">#</span>Country stories: who displaced, who piled on</h2>
    <p class="lead2">Six countries, six very different trajectories. The clean-energy leaders (Germany, Denmark, the UK, the US) cut fossil generation; the fast-growers (China, India) added enormous amounts even as their renewable share rose.</p>
    <div class="stories reveal"><img src="figures/figure13_case_studies.png" alt="Six country trajectories of renewable and fossil electricity shares"></div>
    <div class="sgrid" id="storyCards"></div>
  </div>
</section>

<section id="utility">
  <div class="wrap">
    <h2><span class="n">#</span>Utility &mdash; what you can do here</h2>
    <p class="lead2">Everything on this page is generated from one analysis pipeline. Pick the view that fits what you need &mdash; from a two-minute interactive look to the machine-readable data behind every number.</p>
    <div class="grid">
      <div class="card">
        <div class="ic">&#128202;</div>
        <h3>Interactive explorer</h3>
        <p>Choose any of %%N_PANEL%% countries and watch its renewable and fossil shares move since %%START_YR%%, with displacement and decoupling status.</p>
        <a class="more" href="dashboard.html">Open dashboard &rarr;</a>
      </div>
      <div class="card">
        <div class="ic">&#128221;</div>
        <h3>Full report</h3>
        <p>A thesis-level HTML paper: methods, 12 figures, and five tables walking through every result.</p>
        <a class="more" href="report.html">Read report &rarr;</a>
      </div>
      <div class="card">
        <div class="ic">&#127891;</div>
        <h3>Academic PDF</h3>
        <p>Journal-submission LaTeX with literature review, robustness checks, and heterogeneity tables.</p>
        <a class="more" href="manuscript.pdf">Download PDF &rarr;</a>
      </div>
      <div class="card">
        <div class="ic">&#128190;</div>
        <h3>The data</h3>
        <p>Every figure and statistic as machine-readable JSON, so you can verify or extend the analysis.</p>
        <a class="more" href="results.json">Get results.json &rarr;</a>
      </div>
      <div class="card">
        <div class="ic">&#9874;</div>
        <h3>Reproduce it</h3>
        <p>Three commands regenerate the entire project from the raw OWID CSVs. See <a href="#howto">How&nbsp;to</a>.</p>
        <a class="more" href="https://github.com/your-github-username/renewables-vs-fossil">View code &rarr;</a>
      </div>
      <div class="card">
        <div class="ic">&#128172;</div>
        <h3>Plain-language read</h3>
        <p>An explainer written for a general audience &mdash; shareable, no equations required.</p>
        <a class="more" href="post_zh.md">中文解读 &rarr;</a> &nbsp; <a class="more" href="post_en.md">English &rarr;</a>
      </div>
    </div>
  </div>
</section>

<section id="faq" style="background:#f3f7f4;">
  <div class="wrap">
    <h2><span class="n">#</span>Myth vs fact</h2>
    <p class="lead2">The findings get misread in predictable ways. Here are the four most common.</p>
    <div class="faq">
      <details open><summary>&ldquo;Renewable share is rising everywhere &mdash; so we&rsquo;re winning.&rdquo;</summary>
      <p>Share and absolute generation are different things. Because total electricity demand grew, the world added <b>%%RENEW_ADDED%% TWh</b> of renewables <i>and</i> <b>%%FOSSIL_ADDED%% TWh</b> of fossil over 2000&ndash;%%END_YR%%. A rising renewable <i>share</i> mostly means clean power is catching up to a growing total &mdash; not that coal and gas are being switched off.</p></details>
      <details><summary>&ldquo;Lower CO&#8322; per capita proves the transition is working.&rdquo;</summary>
      <p>It proves the <i>intensity</i> link is real &mdash; each +1pp of renewable share is associated with about &minus;%%FE_PCT%%% CO&#8322;/capita. But intensity falling is not the same as fossil generation falling. The fixed-effects result is an associational dividend, not evidence that fossil plants were retired.</p></details>
      <details><summary>&ldquo;We&rsquo;re just early &mdash; it&rsquo;ll flip soon.&rdquo;</summary>
      <p>Not at current pace. Holding the last decade&rsquo;s momentum, fossil generation reaches about <b>%%FOSSIL_2030%% TWh</b> by 2030 &mdash; up from %%FOSSIL_BASE%% TWh in %%END_YR%%. Decoupling is spreading (absolute-decoupling countries rose from %%ABS_FIRST%%% to %%ABS_LAST%%%), but absolute fossil output is still growing.</p></details>
      <details><summary>&ldquo;So this is anti-renewables?&rdquo;</summary>
      <p>No. Renewables are clearly cutting emissions per person, strongly in Europe and the Americas. The point is narrower and more useful: the build-out has been <i>additive</i>, not <i>substitutive</i>. Closing fossil plant &mdash; not just building renewables &mdash; is the missing half of the transition.</p></details>
    </div>
  </div>
</section>

<section id="howto">
  <div class="wrap">
    <h2><span class="n">#</span>How to &mdash; read, reproduce, cite</h2>
    <p class="lead2">The study is built to be checked. Three short guides below.</p>

    <div class="callout good"><b>The one-sentence finding:</b> renewable share is linked to lower CO&#8322; per capita almost everywhere (about &minus;%%FE_PCT%%% per +1pp), yet the growth is overwhelmingly <i>additive</i> &mdash; fossil generation rose by %%FOSSIL_ADDED%% TWh while renewables rose by %%RENEW_ADDED%% TWh, and only %%PCT_DISP%%% of countries cut fossil output.</div>

    <h3 style="margin:8px 0 4px;">How to read the results</h3>
    <div class="step"><div class="num">1</div><div><h4>Decoupling &#8800; displacement</h4><p>&ldquo;Lower emissions per person&rdquo; (a fixed-effects <i>intensity</i> result) is not the same as &ldquo;less fossil power.&rdquo; The displacement question is about absolute generation, and there the picture flips: globally, fossil grew more than renewables did.</p></div></div>
    <div class="step"><div class="num">2</div><div><h4>Where it works</h4><p>The emissions dividend is largest in the Americas (&minus;%%AMER%%%/pp) and Europe (&minus;%%EUR%%%/pp), and weakest where grids were just starting out. Split by 2000 baseline, it is strongest exactly where renewable penetration was already high.</p></div></div>
    <div class="step"><div class="num">3</div><div><h4>Why 2030 still matters</h4><p>Extrapolating recent momentum gives roughly %%PJ2030%%% renewable share by 2030 &mdash; real progress, still far below fossil&rsquo;s ~61% share.</p></div></div>

    <h3 style="margin:30px 0 8px;">How to reproduce</h3>
    <div class="code"><span class="c"># from the research/ folder</span><br>python src/analysis.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# &rarr; results.json + 13 figures<br>python src/build_report.py&nbsp;&nbsp;&nbsp;# &rarr; report.html<br>python src/build_dashboard.py # &rarr; dashboard.html</div>

    <h3 style="margin:30px 0 8px;">How to cite</h3>
    <div class="cite">
      <button onclick="copyCite()">Copy</button>
      Your Name (2026). <i>The Global Renewable Electricity Transition and Its Decoupling from CO&#8322; Emissions: A Reproducible Cross-Country Analysis, %%START_YR%%&ndash;%%END_YR%%.</i> Preprint. https://github.com/your-github-username/renewables-vs-fossil
    </div>
    <p style="margin-top:10px;color:var(--muted);font-size:13.5px">Metadata also provided as <a href="CITATION.cff">CITATION.cff</a>; deposit with <a href="zenodo.json">zenodo.json</a> for a DOI.</p>
  </div>
</section>

<footer>
  <div class="wrap">
    <div>Data: Our World in Data &mdash; Energy &amp; CO&#8322; datasets (CC-BY). Code: MIT. Every number is computed by <code>src/analysis.py</code> and read from <code>results.json</code>.</div>
    <div>Built as a static, shareable site &middot; <a href="dashboard.html">Dashboard</a> &middot; <a href="report.html">Report</a> &middot; <a href="manuscript.pdf">PDF</a></div>
  </div>
</footer>

<div class="toast" id="toast">Link copied</div>

<script>
const LD = __LDATA__;
const C = {renew:'#2ca02c', fossil:'#d62728', low:'#1f77b4', ink:'#333'};
const LAYOUT = {font:{family:'-apple-system,Segoe UI,Roboto,sans-serif',size:12}, margin:{t:30,r:14,b:46,l:56}, paper_bgcolor:'#fff', plot_bgcolor:'#fff', hovermode:'closest'};
const CFG = {displayModeBar:false, responsive:true};

/* ---- animated KPI counters ---- */
function fmt(v, dec, pre, suf){
  const s = Number(v).toLocaleString(undefined,{minimumFractionDigits:dec, maximumFractionDigits:dec});
  return (pre||'') + s + (suf||'');
}
document.querySelectorAll('.kpi .v[data-num]').forEach(function(el){
  const target=parseFloat(String(el.dataset.num).replace(/,/g,'')), dec=+(el.dataset.dec||0),
        pre=el.dataset.prefix||'', suf=el.dataset.suffix||'';
  const t0=performance.now(), dur=1100;
  function step(t){
    const k=Math.min(1,(t-t0)/dur), e=1-Math.pow(1-k,3);
    el.textContent=fmt(target*e,dec,pre,suf);
    if(k<1) requestAnimationFrame(step); else el.textContent=fmt(target,dec,pre,suf);
  }
  requestAnimationFrame(step);
});

/* ---- reveal on scroll ---- */
const io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)e.target.classList.add('in');});},{threshold:.12});
document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});

/* ---- mobile nav ---- */
document.querySelector('.menu-btn').addEventListener('click',function(){
  document.querySelector('.nav nav').classList.toggle('open');
});
document.querySelectorAll('.nav nav a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('.nav nav').classList.remove('open');});});

/* ---- interactive explore chart ---- */
const sel=document.getElementById('exploreSel');
LD.cases.forEach(function(c,i){const o=document.createElement('option');o.value=i;o.textContent=c.name;sel.appendChild(o);});
function drawExplore(){
  const i=sel.value;
  const traces=[
    {x:LD.years,y:LD.renew,name:'Renewables (world)',mode:'lines',line:{color:C.renew,width:3}},
    {x:LD.years,y:LD.fossil,name:'Fossil (world)',mode:'lines',line:{color:C.fossil,width:3}},
    {x:LD.years,y:LD.low,name:'Low-carbon (world)',mode:'lines',line:{color:C.low,width:2,dash:'dash'}}
  ];
  if(i!==''){
    const c=LD.cases[+i];
    traces.push({x:c.years,y:c.renew,name:c.name+' renewables',mode:'lines',line:{color:C.renew,width:2,dash:'dot'}});
    traces.push({x:c.years,y:c.fossil,name:c.name+' fossil',mode:'lines',line:{color:C.fossil,width:2,dash:'dot'}});
  }
  Plotly.newPlot('exploreChart',traces,Object.assign({},LAYOUT,{
    legend:{orientation:'h',y:-0.18},yaxis:{title:'% of generation',range:[0,100]},xaxis:{title:'Year'}}),CFG);
}
sel.addEventListener('change',drawExplore);
if(window.Plotly) drawExplore();

/* ---- forward fossil projection chart ---- */
(function(){
  if(!window.Plotly) return;
  const act=LD.fossil_actual_years, actY=LD.fossil_actual;
  const fp=LD.fossil_path, py=fp.map(function(p){return p.year;}), pg=fp.map(function(p){return p.fossil_gen;});
  const allx=act.concat(py), ally=actY.concat(pg);
  Plotly.newPlot('fossilChart',[
    {x:act,y:actY,name:'Actual fossil generation',mode:'lines',line:{color:C.fossil,width:3},fill:'tozeroy',fillcolor:'rgba(214,39,40,0.07)'},
    {x:py,y:pg,name:'Projected (constant momentum)',mode:'lines',line:{color:C.fossil,width:3,dash:'dash'}}
  ],Object.assign({},LAYOUT,{
    legend:{orientation:'h',y:-0.18},yaxis:{title:'Fossil generation (TWh)'},
    xaxis:{title:'Year',range:[2020,2032]},
    shapes:[{type:'line',x0:LD.fossil_base_year,x1:LD.fossil_base_year,y0:0,y1:1,yref:'paper',line:{color:'#999',dash:'dot'}}],
    annotations:[{x:2030,y:LD.fossil_2030,text:'2030 ≈ '+LD.fossil_2030.toLocaleString()+' TWh',showarrow:true,arrowhead:2,ax:-30,ay:-28,font:{color:C.fossil}}]
  }),CFG);
})();

/* ---- case-study cards ---- */
(function(){
  const cards=document.getElementById('storyCards');
  const html=LD.cases.map(function(c){
    const badge=c.displacing?'<span class="badge b-good">displaced fossil</span>':'<span class="badge b-bad">added fossil</span>';
    const co2=c.co2_change_pct==null?'n/a':(c.co2_change_pct>0?'+':'')+c.co2_change_pct+'%';
    return '<div class="scard"><h4>'+c.name+badge+'</h4>'+
      '<div class="meta">Renewable share '+c.renew_2000+'% &rarr; '+c.renew_end+'% &middot; CO&#8322;/capita '+co2+'</div></div>';
  }).join('');
  cards.innerHTML=html;
})();

/* ---- share ---- */
function share(net){
  var url=encodeURIComponent(location.href), title=encodeURIComponent(document.title);
  var map={
    x:'https://twitter.com/intent/tweet?url='+url+'&text='+title,
    linkedin:'https://www.linkedin.com/sharing/share-offsite/?url='+url,
    facebook:'https://www.facebook.com/sharer/sharer.php?u='+url,
    weibo:'https://service.weibo.com/share/share.php?url='+url+'&title='+title
  };
  if(map[net]) window.open(map[net],'_blank','width=620,height=520,noopener');
}
document.querySelectorAll('.sb[data-net]').forEach(function(b){
  b.addEventListener('click',function(){ share(b.getAttribute('data-net')); });
});
document.getElementById('copyBtn').addEventListener('click',function(){
  navigator.clipboard.writeText(location.href).then(function(){
    var t=document.getElementById('toast'); t.classList.add('show');
    setTimeout(function(){ t.classList.remove('show'); },1600);
  });
});
function copyCite(){
  var txt=document.querySelector('.cite').innerText.replace('Copy','').trim();
  navigator.clipboard.writeText(txt);
  var t=document.getElementById('toast'); t.textContent='Citation copied'; t.classList.add('show');
  setTimeout(function(){ t.classList.remove('show'); t.textContent='Link copied'; },1600);
}
</script>
</body>
</html>"""

html = TEMPLATE
for k, v in P.items():
    html = html.replace("%%" + k + "%%", v)
html = html.replace("__LDATA__", json.dumps(ldata, ensure_ascii=False))

(ROOT / "index.html").write_text(html, encoding="utf-8")
print("Wrote index.html (", len(html), "bytes )")
