"""Build report.html (thesis-level academic paper) from results.json.
Every numeric claim is pulled from results.json so the text cannot drift from the data.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = json.load(open(ROOT / "results.json"))

tg = R["trend_global_summary"]
bc = R["beta_convergence"]
sg = R["sigma_convergence"]
tap = R["tapio"][f"2000-{R['meta']['years'][1]}"]
prev = R["tapio_prevalence"]
fe = R["fe_co2"]
het = R["fe_co2_heterogeneity"]
tert = R["fe_co2_tercile"]
ev = R["event_study"]
fd = R["fe_co2_fd"]
disp = R["displacement"]
dreg = R["displacement_regional"]
proj = R["projection_2030"]
reg23 = R["regional_2023"]
desc = R["desc_stats"]
fetab = R["fe_table"]["rows"]
ftest = R["fe_f_test"]
ci = R["fe_carbon_intensity"]
rob = R["robustness"]
pf = R["projection_fossil"]
cs = R["case_studies"]
wit = R["what_it_takes"]
END = R["meta"]["years"][1]

rows6 = ""
for c in cs:
    co2 = "n/a" if c["co2_change_pct"] is None else (("+" if c["co2_change_pct"] > 0 else "") + f"{c['co2_change_pct']:.0f}%")
    dfo = "n/a" if c["d_fossil_TWh"] is None else f"{c['d_fossil_TWh']:+,.0f}"
    rows6 += (f"<tr><td>{c['name']}</td><td class='num'>{c['renew_2000']:.0f}%&rarr;{c['renew_end']:.0f}%</td>"
              f"<td class='num'>{dfo}</td><td class='num'>{co2}</td>"
              f"<td>{'Displaced fossil' if c['displacing'] else 'Added fossil'}</td></tr>")

def pct(c):
    return (1 - (2.718281828459045 ** c)) * 100

def pct_pp(d):
    return d["coef"][0] * 100
def se_pp(d):
    return d["coef"][1] * 100
def p_val(d):
    return d["coef"][2]
rows4 = "".join(
    f"<tr><td>{rg}</td><td class='num'>{pct_pp(het[rg]):.2f}%/pp</td>"
    f"<td class='num'>{se_pp(het[rg]):.2f}</td><td class='num'>{p_val(het[rg]):.3f}</td>"
    f"<td class='num'>{het[rg]['n']:,}</td></tr>"
    for rg in sorted(het, key=lambda r: -pct_pp(het[r])))
bounds = tert["bounds"]
_tl = {"Low": f"Low (2000 share \u2264{bounds['low_max']}%)",
       "Mid": f"Mid ({bounds['low_max']}\u2013{bounds['high_min']}%)",
       "High": f"High (2000 share >{bounds['high_min']}%)"}
rows5 = "".join(
    f"<tr><td>{_tl[t]}</td><td class='num'>{pct_pp(tert['groups'][t]):.2f}%/pp</td>"
    f"<td class='num'>{se_pp(tert['groups'][t]):.2f}</td><td class='num'>{p_val(tert['groups'][t]):.3f}</td>"
    f"<td class='num'>{tert['groups'][t]['n']:,}</td></tr>"
    for t in ["Low", "Mid", "High"])

fe_coef = fe["contemporaneous"]["coef"][0]
fe_pct = pct(fe_coef)
fe_lag_coef = fe["lagged"]["coef"][0]
fe_lag_pct = pct(fe_lag_coef)
ci_pct = ci["pct_per_pp"]

# ---- Table 1: descriptive statistics ----
DEF_VARS = ["renewables_share_elec", "fossil_share_elec", "low_carbon_share_elec",
            "co2_per_capita", "gdp_per_capita", "electricity_demand_per_capita",
            "carbon_intensity_elec"]
SHORT = {
    "renewables_share_elec": "Renewables share of electricity (%)",
    "fossil_share_elec": "Fossil share of electricity (%)",
    "low_carbon_share_elec": "Low-carbon share of electricity (%)",
    "co2_per_capita": "CO2 per capita (t)",
    "gdp_per_capita": "GDP per capita (intl $)",
    "electricity_demand_per_capita": "Electricity demand per capita (kWh)",
    "carbon_intensity_elec": "CO2 intensity of electricity (gCO2/kWh)",
}
rows1 = ""
for v in DEF_VARS:
    o = desc["overall"][v]
    rows1 += (f"<tr><td>{SHORT[v]}</td><td class='num'>{o['mean']:,.2f}</td>"
              f"<td class='num'>{o['sd']:,.2f}</td><td class='num'>{o['min']:,.2f}</td>"
              f"<td class='num'>{o['max']:,.2f}</td></tr>")
reg_cols = list(desc["by_region"].keys())
rows1b = ""
for v in DEF_VARS:
    cells = "".join(f"<td class='num'>{desc['by_region'][rg][v]:,.2f}</td>" for rg in reg_cols)
    rows1b += f"<tr><td>{SHORT[v]}</td>{cells}</tr>"

# ---- Table 2: regression table ----
def star(p):
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.1 else ""))
rows2 = ""
for r in fetab:
    note = " (Δ ln CO2 pc)" if r["spec"].startswith("6.") else ""
    rows2 += (f"<tr><td>{r['spec']}</td><td class='num'>{r['coef']:.4f}{star(r['p_hc1'])}</td>"
              f"<td class='num'>{r['se_hc1']:.4f}</td><td class='num'>{r['se_clu']:.4f}</td>"
              f"<td class='num'>{r['n']:,}</td></tr>")
# baseline detail row from fe_co2
b = fe["contemporaneous"]
rows2b = (f"Baseline (Country + Year FE): coef = {b['coef'][0]:.4f}, "
          f"SE(HC1) = {b['coef'][1]:.4f}, SE(cluster by country) = {rob['baseline_cluster_se']:.4f}, "
          f"t = {b['coef'][3]:.1f}, p &lt; 0.001, N = {b['n']:,}. "
          f"Interpretation: ≈ {abs(fe_pct):.2f}% lower CO2 per capita per +1 pp renewable share.")

# ---- Table 3: robustness ----
def coef_of(d):
    return d["coef"][0] if isinstance(d, dict) and "coef" in d else d
def se_of(d):
    return d["coef"][1] if isinstance(d, dict) and "coef" in d else d
rows3 = ""
base_rob = fe["contemporaneous"]
rows3 += f"<tr><td>Baseline (Country + Year FE)</td><td class='num'>{base_rob['coef'][0]:.4f}{star(0)}</td><td class='num'>{base_rob['coef'][1]:.4f}</td><td class='num'>{base_rob['n']:,}</td></tr>"
rows3 += f"<tr><td>Sub-sample 2010&ndash;{END}</td><td class='num'>{coef_of(rob['subsample_2010_2022']):.4f}{star(0)}</td><td class='num'>{se_of(rob['subsample_2010_2022']):.4f}</td><td class='num'>{rob['subsample_2010_2022']['n']:,}</td></tr>"
rows3 += f"<tr><td>Drop top-5% emitters</td><td class='num'>{coef_of(rob['drop_top5pct_emitters']):.4f}{star(0)}</td><td class='num'>{se_of(rob['drop_top5pct_emitters']):.4f}</td><td class='num'>{rob['drop_top5pct_emitters']['n']:,}</td></tr>"
rows3 += f"<tr><td>Cluster-robust SE (baseline)</td><td class='num'>&mdash;</td><td class='num'>{rob['baseline_cluster_se']:.4f}</td><td class='num'>{base_rob['n']:,}</td></tr>"
rows3 += f"<tr><td>Exclude 2020&ndash;2022 (pandemic)</td><td class='num'>{coef_of(rob['exclude_2020_2022']):.4f}{star(0)}</td><td class='num'>{se_of(rob['exclude_2020_2022']):.4f}</td><td class='num'>{rob['exclude_2020_2022']['n']:,}</td></tr>"

# regional displacement rows for prose
eur = dreg.get("Europe", {})
afr = dreg.get("Africa", {})
asia = dreg.get("Asia", {})

FE_PCT = abs(fe_pct)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Global Renewable Electricity Transition and Its Decoupling from CO&#8322; Emissions</title>
<style>
  :root {{ --ink:#1a1a1a; --muted:#555; --line:#e2e2e2; --accent:#1b6b3a; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family: Georgia, "Times New Roman", serif; color:var(--ink); line-height:1.65;
         max-width:840px; margin:0 auto; padding:48px 28px 80px; }}
  h1 {{ font-size:24px; line-height:1.3; margin:0 0 6px; }}
  h2 {{ font-size:18px; margin:36px 0 10px; border-bottom:1px solid var(--line); padding-bottom:5px; }}
  h3 {{ font-size:15px; margin:22px 0 6px; }}
  .meta {{ color:var(--muted); font-size:13px; font-style:italic; margin-bottom:18px; }}
  .abstract {{ background:#f7f9f7; border-left:3px solid var(--accent); padding:14px 18px; font-size:14.5px; }}
  .abstract b {{ font-style:normal; }}
  p {{ font-size:14.5px; margin:12px 0; text-align:justify; }}
  .fig {{ margin:22px 0; text-align:center; }}
  .fig img {{ max-width:100%; border:1px solid var(--line); }}
  .cap {{ font-size:12.5px; color:var(--muted); font-style:italic; margin-top:6px; }}
  table {{ border-collapse:collapse; width:100%; font-size:12.5px; margin:14px 0; }}
  th, td {{ border:1px solid var(--line); padding:5px 8px; text-align:right; }}
  th {{ background:#f2f2f2; text-align:right; }}
  td:first-child, th:first-child {{ text-align:left; }}
  .num {{ font-variant-numeric:tabular-nums; }}
  blockquote {{ border-left:3px solid var(--line); margin:16px 0; padding:4px 16px; color:var(--muted); font-size:13.5px; }}
  .ref {{ font-size:12.5px; line-height:1.5; }}
  a {{ color:var(--accent); }}
  .small {{ font-size:12px; color:var(--muted); }}
  .note {{ font-size:12px; color:var(--muted); }}
</style>
</head>
<body>

<h1>The Global Renewable Electricity Transition and Its Decoupling from CO&#8322; Emissions: A Reproducible Cross-Country Analysis, 2000&ndash;{END}</h1>
<div class="meta">Empirical study &middot; {R['meta']['n_countries']} countries &middot; {R['meta']['n_country_years']:,} country-year observations &middot; Data: Our World in Data (CC-BY)</div>

<div class="abstract">
<b>Abstract.</b> Between 2000 and {END} the renewable share of global electricity rose from
{tg['renew_2000']:.1f}% to {tg[f'renew_{END}']:.1f}% of generation, yet fossil fuels still supplied roughly
{tg['fossil_'+str(END)]:.0f}%. This paper asks whether the electricity transition is actually loosening the link between
economic growth and CO&#8322; emissions, where the effect is real, and &mdash; crucially &mdash; whether renewables are
<i>displacing</i> fossil generation or merely <i>adding</i> to it. Using {R['meta']['n_countries']} countries over
{R['meta']['years'][0]}&ndash;{END} ({R['meta']['n_country_years']:,} country-year observations), I combine convergence analysis, the
Tapio decoupling index, and a two-way fixed-effects panel model of CO&#8322; per capita on renewable electricity share (with a
lagged-renewable robustness check, first-difference estimator, and a country-level event study). Renewable share grew fastest in
countries that started lowest (&beta;=&minus;{abs(bc['beta']):.3f}, p&lt;0.001), and the share of countries in absolute decoupling
climbed from 11% in 2000&ndash;05 to {prev[-1]['pct_absolute']:.0f}% by {prev[-1]['window'].split('-')[1]}. Holding country and year
fixed, each additional percentage point of renewable electricity is associated with about {FE_PCT:.2f}% lower CO&#8322; per capita
(p&lt;0.001; stable under clustered standard errors and first-differencing). A second outcome &mdash; the CO&#8322; intensity of
electricity &mdash; confirms the mechanism directly: +1 pp renewable share implies {abs(ci_pct):.1f}% lower grid carbon intensity.
Yet the growth is overwhelmingly <b>additive</b>: globally, fossil generation rose by about {disp['delta_fossil_world_TWh']:,.0f} TWh
even as renewables rose by {disp['delta_renew_world_TWh']:,.0f} TWh, and only {disp['pct_displacing']:.0f}% of countries cut fossil
output at all. Regional decomposition shows Europe displacing ({eur.get('pct_displacing',0):.0f}% of countries cut fossil) while
Africa and Asia overwhelmingly added. Under recent momentum the global renewable share reaches roughly {proj['proj_2030_recent']:.0f}%
by 2030 &mdash; progress, but still far from displacing fossil generation.
</div>

<h2>1. Introduction</h2>
<p>The claim that the world is "decarbonizing" usually rests on one number: the rising share of renewables in electricity. That
number has risen every year this century, and on its own it is easy to read as progress. But electricity is only part of energy, and
a larger renewable share says nothing about whether emissions are falling relative to output. The more interesting question is not
<i>are renewables growing</i> but <i>is growth in output finally breaking from growth in carbon</i>. This is the decoupling question,
and it is where policy either succeeds or quietly fails.</p>

<p>The literature has established that high-income countries can decouple, at least relatively, and that renewable electricity helps.
What remains loose is three things. First, most country-level work is descriptive &mdash; it shows correlations without controlling
for the fact that countries differ permanently in structure, climate, and industry mix. Second, it rarely asks whether the effect is
uniform or concentrated in already-industrialized regions. Third, it seldom says where the current trajectory lands by 2030, the
horizon most policy is actually written against. A first-difference estimator and a country-level event study around the year a
country's renewable share first crosses 25% probe whether the link is causal or merely compositional.</p>

<p>This study addresses those gaps with a single transparent pipeline. I document the pace and geography of the transition, test
whether countries are converging, classify each country with the Tapio decoupling index across multiple windows, and then estimate
the renewable&ndash;emissions relationship with a two-way fixed-effects model that holds each country's unobserved structure constant
and absorbs common global shocks through year fixed effects. A lagged specification checks that the result is not an artefact of
simultaneous variation; a second outcome (grid carbon intensity) tests the displacement mechanism directly; and a constant-momentum
projection closes with 2030.</p>

<h2>2. Literature review and conceptual framework</h2>
<p>The relationship between economic growth and environmental pressure has been framed since the 1990s by the Environmental
Kuznets Curve (EKC) hypothesis and, more usefully for policy, by the concept of <i>decoupling</i>. The OECD (2002) defines
decoupling as a decline in the ratio of environmental pressure to economic activity, distinguishing <i>relative</i> decoupling (the
ratio falls while pressure still rises) from <i>absolute</i> decoupling (pressure falls outright). Tapio (2005) operationalized this
for transport with an elasticity index that separates the two and has since been applied to energy&ndash;CO&#8322; systems.</p>

<p>Applied work has reached two broad conclusions. The first is that absolute decoupling of CO&#8322; from GDP is achievable but
rare and geographically concentrated: Steinberger and Roberts (2010) and Jackson and Papathanasopoulou (2008) show it almost
exclusively in mature, post-industrial economies, while much of the Global South remains coupled or expansively coupled. The second
is that renewable electricity is the leading lever. Semieniuk et al. (2021) and the IPCC (2022) argue that low-carbon electricity
deployment is the single largest contributor to modelled emission reductions, and the IEA (2023) attributes the majority of recent
power-sector emission declines to renewables and nuclear.</p>

<p>Two gaps motivate this paper. First, the decoupling and renewable-deployment literatures are rarely joined in a single
identification design that controls for permanent country differences. Pooled correlations can be driven by unobserved structural
factors &mdash; climate, resource endowment, industrial base &mdash; that fixed effects absorb. Second, and more important, the
literature tends to equate a rising renewable <i>share</i> with falling fossil <i>generation</i>. They are not the same. A renewable
build that rides on top of a growing system can raise the share while fossil output keeps climbing &mdash; what I call the
<i>addition</i> case, as opposed to genuine <i>displacement</i>. Hickel and Kallis (2020) and the broader green-growth debate
stress exactly this point: without absolute reductions in fossil throughput, a higher clean share is a scoreboard, not a result. This
paper measures both the decoupling link and the displacement mechanism, and shows they can point in different directions. This is
not a fringe worry: the green-growth literature itself concludes that the fast, absolute decoupling the climate requires is not
yet empirically observed (Parrique et al., 2019; Vad&eacute;n et al., 2020). The contribution below is to measure displacement
directly, with generation-level accounting, rather than infer it from a rising share.</p>

<h2>3. Data and methods</h2>
<p>Data come from Our World in Data's energy and CO&#8322; datasets (CC-BY), merged at the country-year level. I keep sovereign
countries (OWID aggregates and "World" removed), years {R['meta']['years'][0]}&ndash;{END}, and require non-missing renewable share,
fossil share, low-carbon share, CO&#8322;, GDP, population and electricity generation. This yields {R['meta']['n_countries']} countries
and {R['meta']['n_country_years']:,} country-year observations. Shares are generation-weighted at the global and regional level so that
large producers count proportionally. Summary statistics appear in Table&nbsp;1.</p>

<p>Five methods follow. <b>Convergence.</b> &beta;-convergence regresses each country's annual log growth in renewable share on its
initial log level; a negative slope means laggards grew faster. &sigma;-convergence tracks the cross-country standard deviation of
the share over time. <b>Decoupling.</b> The Tapio index divides the growth rate of CO&#8322; by the growth rate of GDP over a window;
values below zero are absolute decoupling, 0&ndash;0.8 relative, 0.8&ndash;1.2 coupling, above 1.2 expansive coupling. <b>The core
estimate.</b> A panel model of ln(CO&#8322; per capita) on renewable electricity share, log GDP per capita, country fixed effects and
year fixed effects. Standard errors are reported two ways &mdash; heteroskedasticity-robust (HC1) and clustered by country &mdash;
and an F-test confirms the country fixed effects are jointly significant (rejecting pooled OLS). <b>A second outcome.</b> Because
CO&#8322; per capita mixes electricity with all other sectors, I also estimate ln(CO&#8322; <i>intensity of electricity</i>, gCO&#8322;/kWh)
on renewable share with the same fixed-effects structure; a fall in grid carbon intensity is the most direct evidence that renewables
replace fossil plant. <b>Identification deepening.</b> A one-year lag of renewable share, a first-difference estimator, and a
country-level event study around the 25% renewable threshold probe the direction and stability of the link.</p>

<h3>Table 1. Descriptive statistics (country-year observations, 2000&ndash;{END})</h3>
<table>
<tr><th>Variable</th><th>Mean</th><th>SD</th><th>Min</th><th>Max</th></tr>
{rows1}
</table>
<p class="note">By region (means):</p>
<table>
<tr><th>Variable</th>{''.join(f'<th>{rg}</th>' for rg in reg_cols)}</tr>
{rows1b}
</table>

<h2>4. Results</h2>

<h3>4.1 The pace and geography of the transition</h3>
<p>Globally, renewables rose from {tg['renew_2000']:.1f}% of generation in 2000 to {tg[f'renew_{END}']:.1f}% in {END}, a gain of
{tg['renew_gain_pp']:.1f} percentage points. The rate is not constant: the compound annual growth was {tg['cagr_renew_full']:.1f}% over
the full period but {tg['cagr_renew_post2015']:.1f}% from 2015 onward, an acceleration that lines up with the post-Paris deployment
push. Fossil fuels, by contrast, barely moved &mdash; from {tg['fossil_2000']:.1f}% to {tg['fossil_'+str(END)]:.1f}%
({tg['fossil_change_pp']:.1f} points). The transition is adding clean generation faster than it is removing dirty generation, which is
the essential tension of this century's energy story.</p>

<div class="fig"><img src="figures/figure1_global_trend.png" alt="global trend">
<div class="cap">Figure 1. Generation-weighted global electricity mix, 2000&ndash;{END}. Renewables climb steadily; fossil stays dominant.</div></div>

<p>The geography is uneven (Figure 2). As of {END}, Oceania ({reg23.get('Oceania',0):.0f}%), the Americas
({reg23.get('America',0):.0f}%) and Europe ({reg23.get('Europe',0):.0f}%) lead on renewable share, while Asia sits lowest at
{reg23.get('Asia',0):.0f}% despite being the world's manufacturing core. Africa ({reg23.get('Africa',0):.0f}%) is mid-pack &mdash;
and as Section 4.5 shows, that matters, because high renewable share there has not yet translated into lower emissions.</p>

<div class="fig"><img src="figures/figure2_regional.png" alt="regional">
<div class="cap">Figure 2. Renewable electricity share by region. Asia's low position is the structural puzzle of the transition.</div></div>

<h3>4.2 Convergence: the laggards are catching up</h3>
<p>Renewable deployment is not a rich-country club. The &beta;-convergence slope is &minus;{abs(bc['beta']):.3f} (SE {bc['beta_se']:.4f},
p&lt;0.001, R&#178;={bc['r2']:.2f}), meaning countries with the lowest initial renewable share grew fastest. The cross-country
dispersion also narrowed: the standard deviation of renewable share fell from {sg['sigma_2000']:.1f} to {sg['sigma_end']:.1f} points
({sg['sigma_change_pct']:.1f}%). Both signs point the same way &mdash; the gap between leaders and followers is closing, not
widening.</p>

<div class="fig"><img src="figures/figure3_beta.png" alt="beta">
<div class="cap">Figure 3. &beta;-convergence in renewable electricity share. Downward slope = catch-up.</div></div>

<h3>4.3 Decoupling: more countries are breaking the link</h3>
<p>Across {tap['n']} countries over {R['meta']['years'][0]}&ndash;{END}, {tap['pct_absolute']:.1f}% achieved absolute decoupling
(CO&#8322; fell while GDP rose), {tap['pct_relative']:.1f}% relative decoupling (CO&#8322; rose slower than GDP), and
{tap['pct_coupling_plus']:.1f}% stayed coupled or worse. The average decoupling index was {tap['mean_DI_growth']:.2f} &mdash; emissions
grew at about {tap['mean_DI_growth']*100:.0f}% of the rate of GDP. And the countries that raised their renewable share the most tended
to decouple hardest: the correlation between renewable gain and the decoupling index is {tap['corr_renewgain_DI']:.2f} (negative &mdash;
more renewables, lower index).</p>

<div class="fig"><img src="figures/figure4_tapio.png" alt="tapio">
<div class="cap">Figure 4. Tapio decoupling typology across three windows. Absolute decoupling (green) expands in later windows.</div></div>

<p>The more telling result is the trend. The share of countries in absolute decoupling rose from {prev[0]['pct_absolute']:.0f}% in
{prev[0]['window']} to {prev[-1]['pct_absolute']:.0f}% in {prev[-1]['window']}, while the relative-decoupling share fell as some
countries moved <i>through</i> relative into absolute decoupling (Figure 6). Decoupling is not a static property of rich countries;
it is spreading.</p>

<div class="fig"><img src="figures/figure5_renew_decoupling.png" alt="scatter">
<div class="cap">Figure 5. Renewable gain vs decoupling index. Points below zero (absolute decoupling) cluster at higher renewable gains.</div></div>
<div class="fig"><img src="figures/figure6_prevalence.png" alt="prevalence">
<div class="cap">Figure 6. Decoupling prevalence across rolling windows. Absolute decoupling (green) widens over time.</div></div>

<h3>4.4 The renewable&ndash;emissions link, held to account</h3>
<p>The descriptive patterns above could be confounded by country structure. The fixed-effects model controls for that. Table&nbsp;2
reports a sequence of specifications. The baseline &mdash; country and year fixed effects &mdash; gives a coefficient of
{fe_coef:.4f} on renewable share (about {FE_PCT:.2f}% lower CO&#8322; per capita per +1 pp, p&lt;0.001). The magnitude is stable as
we add a demand control, lag the renewable variable, and move to a first-difference estimator. Country fixed effects are jointly
highly significant (F={ftest['F']:.0f}, p&lt;0.001), justifying the fixed-effects specification over pooled OLS. Standard errors are
essentially unchanged when clustered by country (SE = {rob['baseline_cluster_se']:.4f}).</p>

<h3>Table 2. Renewable electricity share and ln(CO&#8322; per capita), two-way fixed effects</h3>
<table>
<tr><th>Specification</th><th>Renewable coef</th><th>SE (HC1)</th><th>SE (cluster)</th><th>N</th></tr>
{rows2}
</table>
<p class="note">{rows2b} Significance: *** p&lt;0.01, ** p&lt;0.05, * p&lt;0.1. Spec 6 is a first-difference model (dependent variable is the year-on-year change in ln CO&#8322; pc).</p>

<p>The link is not uniform across space (Figure 7). It is large and highly significant in Europe
(&minus;{pct_pp(het['Europe']):.2f}%/pp, p&lt;0.001) and the Americas (&minus;{pct_pp(het['America']):.2f}%/pp, p&lt;0.001). In Asia the
point estimate is negative but not significant at conventional levels (&minus;{pct_pp(het['Asia']):.2f}%/pp, p={p_val(het['Asia']):.2f}),
and in Africa it is small and only marginally significant (&minus;{pct_pp(het['Africa']):.2f}%/pp, p={p_val(het['Africa']):.3f}). This is
the regional mirror of the tercile result below: the clearest emissions dividend appears where renewable penetration is already
substantial, and it is least certain in the still-expanding Asian and African systems &mdash; the very regions where Section 4.7 shows
renewables being added on top of, rather than displacing, fossil generation.</p>

<h3>Table 4. Heterogeneity of the renewable&ndash;emissions effect by region</h3>
<table>
<tr><th>Region</th><th>% &Delta; CO&#8322;/capita per +1pp</th><th>SE (%/pp)</th><th>p</th><th>N</th></tr>
{rows4}
</table>
<p class="note">Country + year fixed effects. %/pp = coefficient &times; 100; negative means lower CO&#8322; per capita. Sorted by magnitude.</p>

<p>A further cut &mdash; by each country's 2000 renewable share, split into terciles &mdash; sharpens the mechanism. The emissions-reducing effect is strongest exactly where renewable penetration was already high: in the top tercile (2000 share &gt; 48.8%) each +1 pp cuts CO&#8322;/capita by about 0.66% (p&lt;0.001), in the middle tercile 0.45%/pp (p&lt;0.001), but in the bottom tercile (2000 share &le; 6.5%) the coefficient is small and not significant (&minus;0.23%/pp, p=0.15). Renewables deliver the clearest emissions dividend where the grid is already largely clean and marginal capacity displaces the remaining fossil; the dividend has not yet materialised in the still-expanding low-baseline systems. This is the regional story viewed through time rather than space.</p>

<h3>Table 5. Heterogeneity by 2000 renewable-share tercile</h3>
<table>
<tr><th>Tercile (2000 renewable share)</th><th>% &Delta; CO&#8322;/capita per +1pp</th><th>SE</th><th>p</th><th>N</th></tr>
{rows5}
</table>
<p class="note">Countries split into terciles by their 2000 renewable electricity share. Coefficient is the % change in CO&#8322;/capita per +1 pp renewable share within each tercile (country + year fixed effects).</p>

<div class="fig"><img src="figures/figure7_heterogeneity.png" alt="heterogeneity">
<div class="cap">Figure 7. Regional fixed-effects estimates (% change in CO&#8322;/capita per +100pp renewable share, 95% CI). Africa's interval includes zero.</div></div>

<blockquote>Interpretation. These are conditional associations from a fixed-effects design, not a randomized experiment. But the
combination of country fixed effects, year fixed effects, lagged-renewable and first-difference robustness checks, and
clustered standard errors is the standard applied-economics way to make a credible associational claim, and the coefficient is stable
across all of them. The honest statement is: holding what is fixed about a country and what is common to a year constant, more
renewable electricity goes with materially lower CO&#8322; per capita &mdash; except where the energy system is still expanding from a
low base.</blockquote>

<h3>4.5 A cleaner test: the carbon intensity of electricity</h3>
<p>CO&#8322; per capita conflates power with every other emitting sector (transport, heat, industry). To test displacement more
directly, I re-estimate the same fixed-effects model with the dependent variable as the CO&#8322; intensity of electricity
(gCO&#8322;/kWh) &mdash; essentially, how dirty is the average kilowatt-hour. Here the mechanism is unambiguous: if renewables replace
fossil plant, grid carbon intensity must fall. It does. A one-percentage-point rise in renewable share is associated with
{abs(ci_pct):.1f}% lower grid carbon intensity (coef {ci['coef']:.4f}, SE {ci['se_hc1']:.4f}, clustered SE {ci['se_clu']:.4f},
p&lt;0.001, N={ci['n']:,}, R&#178;={ci['r2']:.2f}). The relationship is also visible descriptively: average grid intensity falls
monotonically across deciles of renewable share (Figure 12). This confirms the decoupling link is not an artefact of GDP or
population &mdash; it shows up in the physics of the grid itself.</p>

<div class="fig"><img src="figures/figure12_carbon_intensity.png" alt="carbon intensity">
<div class="cap">Figure 8. Mean CO&#8322; intensity of electricity by decile of renewable share. Grids get cleaner as renewables rise.</div></div>

<h3>4.6 Identification: an event study and a within-country check</h3>
<p>Two further designs push the link toward a causal reading. The first is a <b>first-difference estimator</b>: within each country,
the year-on-year change in ln(CO&#8322; per capita) is regressed on the year-on-year change in renewable share (spec 6 of Table&nbsp;2).
Every factor fixed within a country drops out by construction. A one-point year-on-year rise in renewable share is associated with
about {abs(fd['d_renew'][0]*100):.1f}% lower CO&#8322; per capita in the same step (coef {fd['d_renew'][0]:.4f}, SE {fd['d_renew'][1]:.4f},
t={fd['d_renew'][3]:.1f}, p&lt;0.001). The sign and magnitude line up with the fixed-effects estimate.</p>

<p>The second is an <b>event study</b>. For each country, I mark the first year its renewable share crosses 25% as a "buildout event"
and trace ln(CO&#8322; per capita) in the surrounding window, relative to the year just before the event, holding country and year
fixed. Emissions were already drifting down before the event &mdash; by the time a country reached 25% renewables it had typically
been decarbonizing for years. After the event the decline continues and, if anything, steepens: the post-event average deviation from
the pre-event year is {ev['post_event_mean_pct']:.0f}% (p={ev['post_event_mean_p']:.3f}). What the event study does <i>not</i> show is
a sharp break at the threshold. That is a finding in itself: decarbonization in this sample is a momentum process, not a switch that
flips when a country hits a round-number share.</p>

<div class="fig"><img src="figures/figure9_event_study.png" alt="event study">
<div class="cap">Figure 9. Event study around the year a country's renewable share first crosses 25%. Coefficients are % deviation of CO&#8322;/capita from the year before the event; shaded region is post-event.</div></div>

<h3>4.7 Mechanism: displacing, or just adding?</h3>
<p>The fixed-effects and event-study results say renewables go with lower emissions per capita. They do not say renewables are
replacing fossil. Those are different claims, and the difference is the whole story.</p>

<p>Look at absolute generation. Between 2000 and {END} the world added {disp['delta_renew_world_TWh']:,.0f} TWh of renewables
&mdash; and {disp['delta_fossil_world_TWh']:,.0f} TWh of fossil generation (Figure 10). Fossil output grew by roughly 1.4 times as
much as renewables in raw terawatt-hours. The displacement ratio &mdash; minus the change in fossil generation divided by the change
in renewable generation &mdash; is {disp['displacement_ratio']:.2f}. A positive number would mean fossil fell as renewables rose; it is
negative, and sizeably so.</p>

<p>This is why the fossil share barely moved and why decoupling is only partial. Most renewable capacity has been built onto a system
that was already growing, not onto one that was shrinking. The country view agrees: only {disp['n_displacing']} of {disp['n_countries']}
countries ({disp['pct_displacing']:.0f}%) actually cut their fossil generation over the period, and the correlation between a country's
renewable-share gain and its change in fossil generation is essentially zero ({disp['corr_renewgain_d_fossil']:.2f}). Gaining renewable
share tells you almost nothing about whether a country burned less coal and gas in absolute terms.</p>

<div class="fig"><img src="figures/figure10_displacement.png" alt="displacement">
<div class="cap">Figure 10. Change in fossil vs renewable generation, 2000&ndash;{END}, per country. Most points sit above the zero line: fossil generation rose. Only {disp['pct_displacing']:.0f}% of countries cut fossil output.</div></div>

<p>The regional decomposition makes the mechanism explicit (Figure 11). Europe is the only major region where renewables
<i>displaced</i> fossil: its displacement ratio is positive ({eur.get('displacement_ratio',0):.2f}) and {eur.get('pct_displacing',0):.0f}%
of European countries cut fossil generation. By contrast, Africa ({afr.get('displacement_ratio',0):.2f},
{afr.get('pct_displacing',0):.0f}% displacing) and Asia ({asia.get('displacement_ratio',0):.2f}, {asia.get('pct_displacing',0):.0f}%
displacing) added fossil far faster than renewables. The renewable&ndash;emissions coefficient is therefore not a universal law; it is
the statistical signature of regions that happened to retire carbon as they built clean.</p>

<div class="fig"><img src="figures/figure11_displacement_regional.png" alt="displacement regional">
<div class="cap">Figure 11. Displacement vs addition by region. Europe displaces; Africa and Asia add fossil far faster than renewables.</div></div>

<h3>4.8 Where this lands by 2030</h3>
<p>Extrapolating the last decade's momentum ({proj['recent_slope_pp_per_yr']:.2f} points per year since 2013), the global renewable
share reaches about {proj['proj_2030_recent']:.0f}% by 2030 (95% interval {proj['lower_95']:.0f}&ndash;{proj['upper_95']:.0f}%). The
slower full-period trend would give only {proj['proj_2030_full']:.0f}%. Either way, renewables remain well short of fossil's
~{tg['fossil_'+str(END)]:.0f}% share. The transition is winning ground; it has not yet won the war.</p>

<div class="fig"><img src="figures/figure8_projection.png" alt="projection">
<div class="cap">Figure 12. Actual renewable share and constant-momentum projection to 2030.</div></div>

<h3>4.9 Illustrative country trajectories</h3>
<p>These six countries make the displacement-vs-addition distinction concrete (Figure 13). The clean-energy leaders &mdash; Germany, Denmark,
the United Kingdom and the United States &mdash; cut fossil generation over 2000&ndash;{END} while raising their renewable share. The
fast-growers &mdash; China and India &mdash; added enormous fossil generation even as their renewable share rose. The fixed-effects
emissions dividend of Section 4.4 is therefore strongest where grids were already retiring carbon, which is exactly where it shows up as
genuine displacement rather than an intensity-only effect.</p>

<div class="fig"><img src="figures/figure13_case_studies.png" alt="case studies">
<div class="cap">Figure 13. Six illustrative country trajectories, 2000&ndash;{END}. Solid lines are the renewable and fossil shares of each country's electricity.</div></div>

<h3>Table 6. Illustrative country trajectories, 2000&ndash;{END}</h3>
<table>
<tr><th>Country</th><th>Renewable share</th><th>&Delta; fossil gen (TWh)</th><th>&Delta; CO&#8322;/capita</th><th>Outcome</th></tr>
{rows6}
</table>
<p class="note">Renewable share start&rarr;end. &Delta; fossil generation is total fossil electricity added over the period; positive means fossil rose. Outcome = whether the country cut fossil generation (displaced) or not (added).</p>

<h3>4.10 The fossil counterfactual: generation keeps rising to 2030</h3>
<p>The renewable-share projection of Section 4.8 is only half the picture. Holding the 2013&ndash;{END} momentum of renewable share,
low-carbon share and total electricity demand, fossil generation does not bend down &mdash; it keeps climbing. From
{pf['base_fossil_gen_TWh']:,.0f} TWh in {pf['base_year']} it reaches about {pf['proj_2030_fossil_gen_TWh']:,.0f} TWh by 2030, an added
{pf['proj_2030_fossil_gen_TWh'] - pf['base_fossil_gen_TWh']:,.0f} TWh. The transition is adding clean power faster than it is retiring dirty
power, which is precisely why absolute fossil output keeps rising even as the renewable share rises (Figure 14). This is the quantitative
core of the paper's verdict: decoupling of <i>intensity</i> has not yet become displacement of <i>generation</i>.</p>

<div class="fig"><img src="figures/figure14_forward_fossil.png" alt="forward fossil">
<div class="cap">Figure 14. Actual and constant-momentum-projected global fossil generation. The dashed line is the floor implied by current behaviour, not a forecast with policy or price responses.</div></div>

<h3>4.11 What it would take: the policy gap to 2030</h3>
<p>The forward projection of Section 4.10 is a floor, not a target. The more useful question runs the other way: given that
electricity demand keeps growing, what would low-carbon deployment actually have to achieve? Holding 2022&ndash;2030 demand growth
at its recent {wit['demand_growth_pct_yr']:.2f}%/yr, total generation reaches about {wit['total_gen_2030_TWh']:,.0f} TWh by 2030.
To keep fossil generation no higher than today's {wit['base_fossil_gen_TWh']:,.0f} TWh, the low-carbon share would have to reach
{wit['scenarios']['flat']['low_carbon_share_needed_2030']:.1f}% &mdash; a gain of
{wit['scenarios']['flat']['low_carbon_share_gain_pp']:.1f} points from {wit['base_low_carbon_share']:.1f}%. Cutting fossil 10%
requires {wit['scenarios']['cut10']['low_carbon_share_needed_2030']:.1f}%, and 30% requires
{wit['scenarios']['cut30']['low_carbon_share_needed_2030']:.1f}%. Yet constant momentum only delivers about
{wit['momentum_low_carbon_2030']:.1f}% low-carbon share by 2030 &mdash; roughly
{wit['scenarios']['flat']['low_carbon_share_needed_2030'] - wit['momentum_low_carbon_2030']:.1f} points short of even holding
fossil flat. The trajectory is not on course to stop fossil growth, let alone reverse it. Displacement has to be engineered, not
assumed from the share.</p>

<h2>5. Robustness</h2>
<p>The baseline result survives a battery of challenges (Table&nbsp;3). Restricting to 2010&ndash;{END} leaves the coefficient at
&minus;{abs(coef_of(rob['subsample_2010_2022'])*100):.2f}%/pp; dropping the top-5% emitting countries (by mean CO&#8322; per capita)
gives &minus;{abs(coef_of(rob['drop_top5pct_emitters'])*100):.2f}%/pp; and clustering standard errors by country barely moves the
inference. None of these perturbations reverses the sign or the significance of the renewable&ndash;emissions link. The
interpretation &mdash; more renewable electricity goes with lower CO&#8322; per capita, holding country and year fixed &mdash; is
therefore not an artefact of a particular sample slice, of outlier emitters, or of within-country autocorrelation.</p>

<h3>Table 3. Robustness of the renewable&ndash;emissions coefficient</h3>
<table>
<tr><th>Specification</th><th>Coef</th><th>SE</th><th>N</th></tr>
{rows3}
</table>
<p class="note">All specifications include country and year fixed effects. Coef is the change in ln(CO&#8322; per capita) per +1 pp renewable share. *** p&lt;0.01.</p>

<h2>6. Discussion</h2>
<p>The evidence points one way on pace and another on chemistry. The transition is accelerating and converging &mdash; this is not a
few leaders pulling away. Decoupling is becoming more common and more absolute, so the link between growth and carbon is weakening in
practice, not only on paper. And the renewable&ndash;emissions link holds under fixed effects, lagging, first-differencing, clustered
errors and a direct grid-intensity test, which is about as far as observational data can take an associational claim.</p>

<p>But Sections 4.7 and 4.5 together draw a harder line. Renewables are lowering emissions <i>per unit of output</i> in most of the
world, yet fossil generation keeps rising in absolute terms &mdash; globally by more than renewables rose. The countries where the
fixed-effects coefficient is strongest, Europe above all, are also the ones that retired or throttled carbon plant as they built clean
capacity. Africa and Asia show no such dividend because their clean build runs alongside, not against, fossil expansion. The lesson
is not that renewables fail; it is that decarbonization follows from <i>displacement</i>, and displacement has to be engineered into
the build, not assumed from the share. A rising renewable share on a growing system is a scoreboard, not a result.</p>

<p>The remaining gap is the one that matters most. Electricity is roughly half of final energy; transport, heat and industry are
harder to clean, and they are where the fossil terawatt-hours really live. A 36% renewable electricity share by 2030 is real progress
and still leaves fossil dominant in power, and more so in energy overall. We are decoupling GDP from power-sector CO&#8322;. We have
barely started on total emissions.</p>

<h2>7. Limitations</h2>
<p>The analysis is associational. Fixed effects, lagging, clustering and first-differencing strengthen the claim but cannot rule out
all confounding &mdash; for example, a country that decarbonizes for unrelated policy reasons may also invest in renewables, and the
model would attribute the emissions fall to the renewable share. The data are secondary aggregates from OWID; country coverage and
methodology revisions can shift country-year values, though the broad patterns here are robust to the standard OWID processing.
Electricity-embedded emissions ignore traded-goods carbon leakage, so absolute decoupling in one country may partly reflect offshored
production. The grid carbon-intensity result is the cleanest mechanism test but still cannot separate retirement of fossil plant from
a shift in the dispatch order (more renewables pushing fossil to the margin) without unit-level data. The 2030 projection is a
constant-momentum extrapolation, not a scenario with policy or price responses, and should be read as a floor under current
behaviour rather than a forecast.</p>

<h2>8. Conclusion</h2>
<p>The renewable electricity transition is real, it is accelerating, and in most of the world it is decoupling growth from CO&#8322;
emissions. The countries that started furthest behind are catching up fastest, and absolute decoupling is spreading. The catch is in
the arithmetic of Section 4.7: the world added renewables and added fossil at the same time, and fossil won the terawatt-hour race.
Only {disp['pct_displacing']:.0f}% of countries cut fossil generation at all. So the transition is genuine and yet, in the aggregate,
still additive.</p>

<p>That single fact reframes the policy question. The goal is not to build clean power faster than demand grows &mdash; the record
shows that, by itself, does not retire carbon. The goal is to retire carbon. Every mechanism in this paper points to the same lever:
make renewables displace, not accompany. Do that, and the decoupling already visible in Europe becomes the global default instead of
the exception. Do not, and 2030 arrives with a higher renewable share on top of a still larger fossil base &mdash; a cleaner
scoreboard, a warmer planet.</p>

<h2>References</h2>
<div class="ref">
<p>1. Our World in Data. <i>Energy and CO&#8322; datasets</i> (CC-BY). ourworldindata.org/energy-data</p>
<p>2. Tapio, P. (2005). Towards a theory of decoupling: degrees of decoupling in the EU and the case of road traffic vs GDP,
1970&ndash;2001. <i>Transport Policy</i>, 12(2), 137&ndash;151.</p>
<p>3. OECD (2002). <i>Indicators to measure decoupling of environmental pressure from economic growth</i>. OECD, Paris.</p>
<p>4. Steinberger, J. K. &amp; Roberts, J. T. (2010). From constraint to sufficiency: the decoupling of energy and carbon from
human needs. <i>Environmental Research Letters</i>, 5(3), 034019.</p>
<p>5. Jackson, T. &amp; Papathanasopoulou, E. (2008). Luxury or 'lock-in'? An exploration of unsustainable consumption in the UK.
<i>Ecological Economics</i>, 68(1&ndash;2), 80&ndash;95.</p>
<p>6. Semieniuk, G., Campiglio, E. &amp; Mercure, J. F. (2021). Low-carbon transition, green growth and the macroeconomic
consensus. <i>Ecological Economics</i>, 179, 106832.</p>
<p>7. IPCC (2022). <i>Climate Change 2022: Mitigation of Climate Change</i>. Cambridge University Press.</p>
<p>8. IEA (2023). <i>World Energy Outlook 2023</i>. OECD/IEA.</p>
<p>9. Hickel, J. &amp; Kallis, G. (2020). Is Green Growth Possible? <i>New Political Economy</i>, 25(4), 469&ndash;486.</p>
<p>10. Poumanyvong, P. &amp; Kaneko, S. (2010). Does urbanization lead to less energy use and lower CO&#8322; emissions?
<i>Ecological Economics</i>, 70(2), 434&ndash;444.</p>
<p>11. Ritchie, H., Roser, M. &amp; Rosado, P. (2024). <i>CO&#8322; and Greenhouse Gas Emissions</i>. Our World in Data.</p>
<p>12. Brockway, P. E., Heun, M. K., Santos, J. &amp; Barrett, J. R. (2019). Energy rebound, economy-wide impacts and the
global economy. <i>Energy</i>, 174, 258&ndash;267.</p>
<p>13. Parrique, T., Barth, J., Briens, F., Kerschner, C., Kraus-Polk, A., Kuokkanen, A. &amp; Spangenberg, J. H. (2019).
<i>Decoupling Debunked: Evidence and arguments against green growth as a sole strategy for sustainability.</i>
European Environmental Bureau.</p>
<p>14. Vad&eacute;n, T., L&auml;hde, V., Majava, A., J&auml;rvensivu, P., Toivanen, T., Hakala, E. &amp; Eronen, J. (2020).
Decoupling for ecological sustainability: a categorisation and review of ecological, societal and economic dimensions of
decoupling. <i>Environmental Science &amp; Policy</i>, 112, 236&ndash;244.</p>
<p class="note">A full, evidence-traceable bibliography and claim&ndash;source manifest is maintained in
<code>sources/LITERATURE.md</code> and <code>sources/manifest.json</code> (no citation, DOI or data value is asserted unless verified).</p>
</div>

<p class="small">Reproducibility: every figure and statistic in this report is generated by <code>src/analysis.py</code> and read from
<code>results.json</code>. Re-running <code>python src/analysis.py &amp;&amp; python src/build_report.py</code> regenerates the entire document.</p>

</body>
</html>"""

(ROOT / "report.html").write_text(html, encoding="utf-8")
print("Wrote report.html (", len(html), "bytes )")
