"""
Reproducible analysis pipeline for:
'The Global Renewable Electricity Transition and Its Decoupling from CO2 Emissions:
 A Reproducible Cross-Country Analysis, 2000-2022'

Data: Our World in Data — Energy (owid-energy-data.csv) + CO2 (owid-co2-data.csv), CC-BY.
Outputs:
  - ../results.json   (every number in the paper lives here; build_report.py reads only this)
  - ../figures/*.png

Methodology (transparent, standard applied-econometrics toolkit):
  1. Descriptive statistics (Table 1): levels of the main variables overall and by region.
  2. Descriptive trends: generation-weighted global & regional renewable/fossil/low-carbon shares.
  3. beta- and sigma-convergence of renewable electricity share across countries.
  4. Panel regressions: drivers of renewable share (pooled OLS + country FE) and an EKC check.
  5. Tapio decoupling index at country level over multiple windows + prevalence trend.
  6. CORE — two-way fixed-effects panel of CO2 per capita on renewable share (country + year FE),
     with (a) a demand control, (b) a lagged-renewable robustness check, (c) cluster-robust SE,
     (d) an F-test that fixed effects are jointly significant, (e) a first-difference estimator,
     (f) a country-level event study, and (g) a SECOND outcome: the CO2 intensity of electricity
     (carbon_intensity_elec), the most direct test of whether renewables displace fossil plant.
  7. Mechanism: displacement vs addition of absolute generation, decomposing by region.
  8. Robustness: subsample (2010-2022), dropping extreme emitters, alternative decoupling windows.
  9. 2030 projection of the global renewable share (constant-momentum, uncertainty band).
"""
import json
import numpy as np
import pandas as pd
import country_converter as coco
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sstats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "owid-energy-data.csv"
CO2 = ROOT / "data" / "owid-co2-data.csv"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
RES = {}

START = 2000
END = None
TT = None

# --------------------------------------------------------------------------- #
# 0. Load & clean
# --------------------------------------------------------------------------- #
print("Loading OWID data ...")
df = pd.read_csv(DATA)
co2 = pd.read_csv(CO2, usecols=["iso_code", "year", "co2", "co2_per_capita"])
co2["co2"] = pd.to_numeric(co2["co2"], errors="coerce")
co2["co2_per_capita"] = pd.to_numeric(co2["co2_per_capita"], errors="coerce")

df = df[df["iso_code"].notna()].copy()
df = df[~df["iso_code"].astype(str).str.startswith("OWID")].copy()
df = df[(df["year"] >= START)].copy()
df = df.merge(co2, on=["iso_code", "year"], how="inner")

need = ["renewables_share_elec", "fossil_share_elec", "low_carbon_share_elec",
        "co2", "gdp", "population", "electricity_generation"]
for c in need:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df.dropna(subset=need).copy()
END = int(df["year"].max())
TT = END - START

df["gdp_per_capita"] = df["gdp"] / df["population"]
# OWID reports co2 in million tonnes; convert to tonnes per capita (population is in persons)
df["co2_per_capita"] = df["co2"] * 1e6 / df["population"]
df["carbon_intensity_elec"] = pd.to_numeric(df["carbon_intensity_elec"], errors="coerce")
df["electricity_demand_per_capita"] = pd.to_numeric(df["electricity_demand_per_capita"], errors="coerce")
try:
    df["region"] = coco.convert(df["iso_code"].tolist(), src="ISO3", to="continent")
except Exception:
    df["region"] = coco.convert(df["iso_code"].tolist(), src="ISO3", to="continent")
df = df[df["region"].notna() & (df["region"] != "not found")].copy()

cov = df.groupby("iso_code")["year"].nunique()
countries = cov[cov >= (TT + 1 - 3)].index
df = df[df["iso_code"].isin(countries)].copy()
df = df.sort_values(["iso_code", "year"]).reset_index(drop=True)
print(f"  countries kept: {df['iso_code'].nunique()}, country-year rows: {len(df):,}")

RES["meta"] = {
    "source": "Our World in Data — Energy and CO2 datasets (owid-energy-data.csv, owid-co2-data.csv), CC-BY",
    "years": [START, END],
    "n_countries": int(df["iso_code"].nunique()),
    "n_country_years": int(len(df)),
    "variables": ["renewables_share_elec", "fossil_share_elec", "low_carbon_share_elec",
                  "co2_per_capita", "gdp_per_capita", "electricity_demand_per_capita",
                  "carbon_intensity_elec"],
}

# --------------------------------------------------------------------------- #
# 1. Descriptive statistics (Table 1)
# --------------------------------------------------------------------------- #
print("Descriptive statistics ...")
DESC_VARS = ["renewables_share_elec", "fossil_share_elec", "low_carbon_share_elec",
             "co2_per_capita", "gdp_per_capita", "electricity_demand_per_capita",
             "carbon_intensity_elec"]
dd = df.dropna(subset=DESC_VARS).copy()
desc = {"vars": DESC_VARS, "labels": {
    "renewables_share_elec": "Renewables share of electricity (%)",
    "fossil_share_elec": "Fossil share of electricity (%)",
    "low_carbon_share_elec": "Low-carbon share of electricity (%)",
    "co2_per_capita": "CO2 per capita (t)",
    "gdp_per_capita": "GDP per capita (2022 PPP-adjusted units)",
    "electricity_demand_per_capita": "Electricity demand per capita (kWh)",
    "carbon_intensity_elec": "CO2 intensity of electricity (gCO2/kWh)"},
    "overall": {}, "by_region": {}}
for v in DESC_VARS:
    desc["overall"][v] = {
        "mean": round(float(dd[v].mean()), 3),
        "sd": round(float(dd[v].std()), 3),
        "min": round(float(dd[v].min()), 3),
        "max": round(float(dd[v].max()), 3),
    }
for rg, g in dd.groupby("region"):
    desc["by_region"][rg] = {v: round(float(g[v].mean()), 3) for v in DESC_VARS}
RES["desc_stats"] = desc

# --------------------------------------------------------------------------- #
# 2. Descriptive trends
# --------------------------------------------------------------------------- #
print("Descriptive trends ...")
ann = df.groupby("year").apply(
    lambda g: pd.Series({
        "renew_share": np.average(g["renewables_share_elec"], weights=g["electricity_generation"]),
        "fossil_share": np.average(g["fossil_share_elec"], weights=g["electricity_generation"]),
        "low_carbon_share": np.average(g["low_carbon_share_elec"], weights=g["electricity_generation"]),
        "total_gen": g["electricity_generation"].sum(),
    }), include_groups=False
)
RES["trend_global"] = {
    "years": [int(y) for y in ann.index.tolist()],
    "renew_share": [round(float(v), 3) for v in ann["renew_share"].tolist()],
    "fossil_share": [round(float(v), 3) for v in ann["fossil_share"].tolist()],
    "low_carbon_share": [round(float(v), 3) for v in ann["low_carbon_share"].tolist()],
    "total_gen": [round(float(v), 0) for v in ann["total_gen"].tolist()],
}
r0, r1 = ann["renew_share"].loc[START], ann["renew_share"].loc[END]
f0, f1 = ann["fossil_share"].loc[START], ann["fossil_share"].loc[END]
cagr_full = round(float(((r1 / r0) ** (1 / TT) - 1) * 100), 2)
cagr_post15 = round(float(((ann["renew_share"].loc[END] / ann["renew_share"].loc[2015]) ** (1 / (END - 2015)) - 1) * 100), 2)
RES["trend_global_summary"] = {
    "renew_2000": round(float(r0), 2), f"renew_{END}": round(float(r1), 2),
    "renew_gain_pp": round(float(r1 - r0), 2),
    "fossil_2000": round(float(f0), 2), f"fossil_{END}": round(float(f1), 2),
    "fossil_change_pp": round(float(f1 - f0), 2),
    "cagr_renew_full": cagr_full,
    "cagr_renew_post2015": cagr_post15,
}

reg = df.pivot_table(index="year", columns="region", values="renewables_share_elec", aggfunc="mean")
RES["trend_regional"] = {
    "years": [int(y) for y in reg.index.tolist()],
    "regions": reg.columns.tolist(),
    "series": {r: [round(float(v), 2) for v in reg[r].tolist()] for r in reg.columns},
}
RES["regional_2023"] = {r: round(float(reg[r].loc[END]), 2) for r in reg.columns}

# --------------------------------------------------------------------------- #
# 3. Convergence
# --------------------------------------------------------------------------- #
print("Convergence analysis ...")
panel = df.pivot_table(index="iso_code", columns="year", values="renewables_share_elec")
valid = panel.dropna(subset=[2000, END]).copy()
valid = valid[valid[2000] > 0]
s0, s1 = valid[2000], valid[END]
y = (np.log(s1 / s0) / TT)
x = np.log(s0)
bdf = pd.DataFrame({"y": y, "x": x}).dropna()
X = sm.add_constant(bdf["x"])
beta_mod = sm.OLS(bdf["y"], X).fit()
RES["beta_convergence"] = {
    "n": int(len(bdf)),
    "beta": round(float(beta_mod.params["x"]), 5),
    "beta_se": round(float(beta_mod.bse["x"]), 5),
    "beta_p": round(float(beta_mod.pvalues["x"]), 4),
    "r2": round(float(beta_mod.rsquared), 3),
    "interpretation": "negative beta => lower initial share grows faster (convergence)" if beta_mod.params["x"] < 0 else "positive beta => divergence",
}
sig = panel.dropna().std(axis=0)
RES["sigma_convergence"] = {
    "sigma_2000": round(float(sig.loc[2000]), 2),
    "sigma_end": round(float(sig.loc[END]), 2),
    "sigma_change_pct": round(float((sig.loc[END] / sig.loc[2000] - 1) * 100), 2),
}

# --------------------------------------------------------------------------- #
# 4. Panel regression: drivers of renewable share + EKC
# --------------------------------------------------------------------------- #
print("Panel regression (renewable share drivers) ...")
m = df.dropna(subset=["renewables_share_elec", "gdp_per_capita"]).copy()
m["log_gdp_pc"] = np.log(m["gdp_per_capita"].clip(lower=1))
m["year_c"] = m["year"] - 2000
pooled = smf.ols("renewables_share_elec ~ log_gdp_pc + year_c + C(region)", data=m).fit(cov_type="HC1")
fe = smf.ols("renewables_share_elec ~ log_gdp_pc + year_c + C(iso_code)", data=m).fit(cov_type="HC1")
RES["panel_renew"] = {
    "n": int(len(m)),
    "pooled": {"log_gdp_pc": [round(float(pooled.params["log_gdp_pc"]), 3), round(float(pooled.bse["log_gdp_pc"]), 3), round(float(pooled.pvalues["log_gdp_pc"]), 4)],
               "year_c": [round(float(pooled.params["year_c"]), 3), round(float(pooled.bse["year_c"]), 3), round(float(pooled.pvalues["year_c"]), 4)],
               "r2": round(float(pooled.rsquared), 3)},
    "fe": {"log_gdp_pc": [round(float(fe.params["log_gdp_pc"]), 3), round(float(fe.bse["log_gdp_pc"]), 3), round(float(fe.pvalues["log_gdp_pc"]), 4)],
           "year_c": [round(float(fe.params["year_c"]), 3), round(float(fe.bse["year_c"]), 3), round(float(fe.pvalues["year_c"]), 4)],
           "r2": round(float(fe.rsquared), 3)},
}

e = df.dropna(subset=["co2_per_capita", "gdp_per_capita"]).copy()
e["log_gdp_pc"] = np.log(e["gdp_per_capita"].clip(lower=1))
e["log_gdp_pc2"] = e["log_gdp_pc"] ** 2
ekc = smf.ols("co2_per_capita ~ log_gdp_pc + log_gdp_pc2 + C(region)", data=e).fit(cov_type="HC1")
RES["panel_ekc"] = {
    "n": int(len(e)),
    "log_gdp_pc": [round(float(ekc.params["log_gdp_pc"]), 3), round(float(ekc.bse["log_gdp_pc"]), 3), round(float(ekc.pvalues["log_gdp_pc"]), 4)],
    "log_gdp_pc2": [round(float(ekc.params["log_gdp_pc2"]), 3), round(float(ekc.bse["log_gdp_pc2"]), 3), round(float(ekc.pvalues["log_gdp_pc2"]), 4)],
    "r2": round(float(ekc.rsquared), 3),
    "turning_point_gdp_pc": round(float(np.exp(-ekc.params["log_gdp_pc"] / (2 * ekc.params["log_gdp_pc2"]))), 1),
}

# --------------------------------------------------------------------------- #
# 5. Tapio decoupling index (country level, multiple windows)
# --------------------------------------------------------------------------- #
print("Tapio decoupling ...")
def tapio(start, end):
    p = df.pivot_table(index="iso_code", columns="year", values=["gdp", "co2", "renewables_share_elec"])
    g0, g1 = p[("gdp", start)], p[("gdp", end)]
    c0, c1 = p[("co2", start)], p[("co2", end)]
    r0, r1 = p[("renewables_share_elec", start)], p[("renewables_share_elec", end)]
    out = pd.DataFrame({"gdp0": g0, "gdp1": g1, "co2_0": c0, "co2_1": c1, "re0": r0, "re1": r1}).dropna()
    out = out[(out.gdp0 > 0) & (out.gdp1 > 0) & (out.co2_0 > 0) & (out.co2_1 > 0)]
    g_growth = (out.gdp1 - out.gdp0) / out.gdp0
    e_growth = (out.co2_1 - out.co2_0) / out.co2_0
    out["g_growth"], out["e_growth"] = g_growth, e_growth
    out["DI"] = np.where(g_growth > 0, e_growth / g_growth, np.nan)
    out["re_gain"] = out.re1 - out.re0

    def cls(row):
        g, em = row.g_growth, row.e_growth
        if g <= 0:
            return "Recessionary (GDP falling)"
        if em < 0:
            return "Absolute decoupling"
        if em < 0.8 * g:
            return "Relative decoupling"
        if em <= 1.2 * g:
            return "Coupling"
        return "Expansive coupling"
    out["cat"] = out.apply(cls, axis=1)
    return out

windows = {f"2000-{END}": (2000, END), f"2010-{END}": (2010, END), f"2015-{END}": (2015, END)}
RES["tapio"] = {}
for label, (s, en) in windows.items():
    d = tapio(s, en)
    counts = d["cat"].value_counts().to_dict()
    growth = d[d.g_growth > 0]
    sub = growth.dropna(subset=["DI", "re_gain"])
    corr = float(np.corrcoef(sub["re_gain"], sub["DI"])[0, 1]) if len(sub) > 2 else None
    RES["tapio"][label] = {
        "n": int(len(d)),
        "counts": {k: int(v) for k, v in counts.items()},
        "pct_absolute": round(float((d["cat"] == "Absolute decoupling").mean() * 100), 1),
        "pct_relative": round(float((d["cat"] == "Relative decoupling").mean() * 100), 1),
        "pct_coupling_plus": round(float((d["cat"].isin(["Coupling", "Expansive coupling"])).mean() * 100), 1),
        "mean_DI_growth": round(float(growth["DI"].mean()), 3),
        "corr_renewgain_DI": round(float(corr), 3) if corr is not None else None,
        "n_corr": int(len(sub)),
    }

print("Decoupling prevalence trend ...")
roll_windows = [(2000, 2005), (2005, 2010), (2010, 2015), (2015, 2020), (max(START, END - 5), END)]
prev = []
for s, en in roll_windows:
    try:
        d = tapio(s, en)
        prev.append({
            "window": f"{s}-{en}",
            "n": int(len(d)),
            "pct_absolute": round(float((d["cat"] == "Absolute decoupling").mean() * 100), 1),
            "pct_relative": round(float((d["cat"] == "Relative decoupling").mean() * 100), 1),
        })
    except Exception:
        continue
RES["tapio_prevalence"] = prev

d_full = tapio(2000, END)
RES["decouple_scatter"] = {
    "re_gain": [round(float(v), 2) for v in d_full["re_gain"].tolist()],
    "DI": [None if pd.isna(v) else round(float(v), 3) for v in d_full["DI"].tolist()],
    "cat": d_full["cat"].tolist(),
}
top = d_full.sort_values("re_gain", ascending=False).head(10)
RES["top_movers"] = [
    {"iso": i, "re_gain": round(float(r.re_gain), 1),
     "DI": (None if pd.isna(r.DI) else round(float(r.DI), 2)), "cat": r["cat"]}
    for i, r in top.iterrows()
]

# --------------------------------------------------------------------------- #
# 6. CORE: two-way FE panel regression of CO2 per capita on renewable share
# --------------------------------------------------------------------------- #
print("Two-way FE regression (CO2 ~ renewable share) ...")
reg_df = df.dropna(subset=["co2_per_capita", "renewables_share_elec", "gdp_per_capita"]).copy()
reg_df["log_co2_pc"] = np.log(reg_df["co2_per_capita"].clip(lower=1e-6))
reg_df["log_gdp_pc"] = np.log(reg_df["gdp_per_capita"].clip(lower=1))
reg_df["log_elec_dem_pc"] = np.log(reg_df["electricity_demand_per_capita"].clip(lower=1))
reg_df["renew_lag1"] = reg_df.groupby("iso_code")["renewables_share_elec"].shift(1)
reg_df["year_f"] = reg_df["year"].astype(int).astype(str)

def coef_block(mod, var):
    return {
        "coef": [round(float(mod.params[var]), 5), round(float(mod.bse[var]), 5),
                 round(float(mod.pvalues[var]), 5), round(float(mod.tvalues[var]), 3)],
        "n": int(mod.nobs),
        "r2": round(float(mod.rsquared), 3),
        "n_groups": int(mod.df_resid),
    }

base = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
               data=reg_df).fit(cov_type="HC1")
lag = smf.ols("log_co2_pc ~ renew_lag1 + log_gdp_pc + C(iso_code) + C(year_f)",
              data=reg_df.dropna(subset=["renew_lag1"])).fit(cov_type="HC1")
RES["fe_co2"] = {
    "contemporaneous": coef_block(base, "renewables_share_elec"),
    "lagged": coef_block(lag, "renew_lag1"),
    "note": "Dependent = ln(CO2 per capita). Coefficient on renewable share (pp) is the "
            "approx. % change in CO2/capita per +1 percentage-point of renewable electricity share, "
            "net of country-specific fixed effects and common time shocks.",
}

# heterogeneity by region
het = {}
for rg in reg_df["region"].dropna().unique():
    sub = reg_df[reg_df["region"] == rg]
    if sub["iso_code"].nunique() < 5 or len(sub) < 50:
        continue
    mm = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
                 data=sub).fit(cov_type="HC1")
    het[rg] = coef_block(mm, "renewables_share_elec")
RES["fe_co2_heterogeneity"] = het

# heterogeneity by baseline (2000) renewable-share tercile -- a clean, data-internal
# mechanism test: does each extra pp of renewables cut emissions most where the grid
# is still fossil-heavy (low baseline renewable share)?
base_share = (df[df["year"] == START].set_index("iso_code")["renewables_share_elec"].dropna())
reg_df["baseline_renew_2000"] = reg_df["iso_code"].map(base_share)
b1, b2 = reg_df["baseline_renew_2000"].quantile([1/3, 2/3])
def _terc(x):
    if pd.isna(x):
        return None
    if x <= b1:
        return "Low"
    if x <= b2:
        return "Mid"
    return "High"
reg_df["renew_tercile"] = reg_df["baseline_renew_2000"].apply(_terc)
tert = {}
for t in ["Low", "Mid", "High"]:
    sub = reg_df[reg_df["renew_tercile"] == t]
    if sub["iso_code"].nunique() < 5 or len(sub) < 50:
        continue
    mm = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
                 data=sub).fit(cov_type="HC1")
    tert[t] = coef_block(mm, "renewables_share_elec")
RES["fe_co2_tercile"] = {
    "bounds": {"low_max": round(float(b1), 1), "high_min": round(float(b2), 1)},
    "groups": tert,
    "note": "Countries split into terciles by their 2000 renewable electricity share. "
            "Coefficient is the % change in CO2/capita per +1 pp renewable share within each tercile.",
}

# ---- multi-specification regression table (with cluster-robust SE + F-test) ----
print("Regression table: pooled / FE / +controls / lag / cluster ...")
def fit_spec(formula, data, var, groups):
    m_hc1 = smf.ols(formula, data=data).fit(cov_type="HC1")
    m_clu = smf.ols(formula, data=data).fit(cov_type="cluster", cov_kwds={"groups": groups})
    return {
        "coef": round(float(m_hc1.params[var]), 5),
        "se_hc1": round(float(m_hc1.bse[var]), 5),
        "se_clu": round(float(m_clu.bse[var]), 5),
        "p_hc1": round(float(m_hc1.pvalues[var]), 5),
        "n": int(m_hc1.nobs),
        "r2": round(float(m_hc1.rsquared), 3),
    }

rhs = "renewables_share_elec + log_gdp_pc"
specs = []
specs.append(("1. Pooled OLS", f"log_co2_pc ~ {rhs}", "renewables_share_elec", reg_df))
specs.append(("2. Country FE", f"log_co2_pc ~ {rhs} + C(iso_code)", "renewables_share_elec", reg_df))
specs.append(("3. Country + Year FE (baseline)", f"log_co2_pc ~ {rhs} + C(iso_code) + C(year_f)", "renewables_share_elec", reg_df))
specs.append(("4. + Demand control", f"log_co2_pc ~ {rhs} + log_elec_dem_pc + C(iso_code) + C(year_f)", "renewables_share_elec", reg_df))
specs.append(("5. Lagged renewable", f"log_co2_pc ~ renew_lag1 + log_gdp_pc + C(iso_code) + C(year_f)", "renew_lag1", reg_df.dropna(subset=["renew_lag1"])))
specs.append(("6. First-difference", "d_log_co2 ~ d_renew + d_log_gdp", "d_renew", None))  # filled below

table_rows = []
for name, formula, var, data in specs[:-1]:
    table_rows.append({"spec": name, **fit_spec(formula, data, var, data["iso_code"])})

# first-difference spec
fd = reg_df.dropna(subset=["log_co2_pc", "renewables_share_elec", "log_gdp_pc"]).sort_values(["iso_code", "year"]).copy()
fd["d_log_co2"] = fd.groupby("iso_code")["log_co2_pc"].diff()
fd["d_renew"] = fd.groupby("iso_code")["renewables_share_elec"].diff()
fd["d_log_gdp"] = fd.groupby("iso_code")["log_gdp_pc"].diff()
fdm = smf.ols("d_log_co2 ~ d_renew + d_log_gdp", data=fd.dropna()).fit(cov_type="HC1")
fd_clu = smf.ols("d_log_co2 ~ d_renew + d_log_gdp", data=fd.dropna()).fit(cov_type="cluster", cov_kwds={"groups": fd.dropna()["iso_code"]})
table_rows.append({"spec": "6. First-difference",
                   "coef": round(float(fdm.params["d_renew"]), 5),
                   "se_hc1": round(float(fdm.bse["d_renew"]), 5),
                   "se_clu": round(float(fd_clu.bse["d_renew"]), 5),
                   "p_hc1": round(float(fdm.pvalues["d_renew"]), 5),
                   "n": int(fdm.nobs), "r2": round(float(fdm.rsquared), 3)})
RES["fe_table"] = {"rows": table_rows,
                   "note": "Dependent variable: ln(CO2 per capita) in specs 1-5; year-on-year "
                           "change in ln(CO2 per capita) in spec 6. Coefficient on renewable "
                           "electricity share (increase of +1 pp). SE: HC1 heteroskedasticity-robust "
                           "and cluster-robust at the country level."}

# F-test: are country fixed effects jointly significant?
pooled_nofe = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc", data=reg_df).fit()
q = reg_df["iso_code"].nunique() - 1
Fstat = ((pooled_nofe.ssr - base.ssr) / q) / (base.ssr / base.df_resid)
Fp = float(sstats.f.sf(Fstat, q, base.df_resid))
RES["fe_f_test"] = {
    "F": round(float(Fstat), 2), "df1": int(q), "df2": int(base.df_resid),
    "p": round(Fp, 6),
    "interpretation": "Country fixed effects are jointly significant (rejects pooled OLS).",
}

# ---- SECOND OUTCOME: CO2 intensity of electricity (direct displacement test) ----
print("Carbon-intensity-of-electricity outcome ...")
ci = reg_df.dropna(subset=["carbon_intensity_elec", "renewables_share_elec", "gdp_per_capita"]).copy()
ci = ci[ci["carbon_intensity_elec"] > 0].copy()
ci["log_ci"] = np.log(ci["carbon_intensity_elec"].clip(lower=1e-3))
ci_mod = smf.ols("log_ci ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
                 data=ci).fit(cov_type="HC1")
ci_clu = smf.ols("log_ci ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
                 data=ci).fit(cov_type="cluster", cov_kwds={"groups": ci["iso_code"]})
RES["fe_carbon_intensity"] = {
    "coef": round(float(ci_mod.params["renewables_share_elec"]), 5),
    "se_hc1": round(float(ci_mod.bse["renewables_share_elec"]), 5),
    "se_clu": round(float(ci_clu.bse["renewables_share_elec"]), 5),
    "p_hc1": round(float(ci_mod.pvalues["renewables_share_elec"]), 5),
    "n": int(ci_mod.nobs), "r2": round(float(ci_mod.rsquared), 3),
    "pct_per_pp": round((1 - (np.e ** ci_mod.params["renewables_share_elec"])) * 100, 2),
    "note": "Dependent = ln(CO2 intensity of electricity, gCO2/kWh). This is the most direct test of "
            "displacement: if renewables replace fossil plant, grid carbon intensity falls. Coefficient "
            "is % change in intensity per +1 pp of renewable share, country + year FE.",
}

# --------------------------------------------------------------------------- #
# 6b. Identification deepening: event study + first-difference robustness
# --------------------------------------------------------------------------- #
print("Event study: renewable buildout as a country-specific shock ...")
THR = 25.0
ev_frames = []
for iso, g in reg_df.sort_values("year").groupby("iso_code"):
    g = g.dropna(subset=["renewables_share_elec", "log_co2_pc", "log_gdp_pc"])
    crossed = g[g["renewables_share_elec"] >= THR]
    if len(crossed) == 0:
        continue
    ev_year = int(crossed["year"].min())
    gg = g.copy()
    gg["rel_year"] = gg["year"] - ev_year
    gg = gg[gg["rel_year"].between(-6, 6)]
    ev_frames.append(gg)
ev = pd.concat(ev_frames, ignore_index=True)
ev = ev.groupby("iso_code").filter(lambda x: (x["rel_year"] < 0).sum() >= 2 and (x["rel_year"] > 0).sum() >= 2)
ev["rel_year_f"] = ev["rel_year"].astype(int).astype(str)
es = smf.ols("log_co2_pc ~ C(rel_year_f, Treatment(reference='-1')) + C(iso_code) + C(year_f)",
             data=ev).fit(cov_type="HC1")
rel_years = sorted({int(k) for k in ev["rel_year_f"].unique() if k != '-1'})
es_coef, es_se, es_ci = [], [], []
for ry in rel_years:
    key = f"C(rel_year_f, Treatment(reference='-1'))[T.{ry}]"
    if key in es.params:
        es_coef.append(round(float(es.params[key]) * 100, 3))
        es_se.append(round(float(es.bse[key]) * 100, 3))
        es_ci.append(round(1.96 * float(es.bse[key]) * 100, 3))
    else:
        es_coef.append(None); es_se.append(None); es_ci.append(None)
post_keys = [f"C(rel_year_f, Treatment(reference='-1'))[T.{ry}]" for ry in rel_years if ry >= 0]
post_vals = [es.params[k] for k in post_keys if k in es.params]
es_post_mean = round(float(np.mean(post_vals)) * 100, 2) if post_vals else None
es_post_p = round(float(es.pvalues[post_keys[0]]), 4) if post_keys and post_keys[0] in es.pvalues else None
RES["event_study"] = {
    "threshold": THR,
    "n_countries": int(ev["iso_code"].nunique()),
    "n_obs": int(len(ev)),
    "rel_years": rel_years,
    "coef_pct": es_coef,
    "se_pct": es_se,
    "ci95_pct": es_ci,
    "post_event_mean_pct": es_post_mean,
    "post_event_mean_p": es_post_p,
    "note": "Each country's first year above 25% renewable share = event year. Coefficients are "
            "% deviation of ln(CO2/capita) from the year immediately before the event (rel_year=-1), "
            "net of country and year fixed effects.",
}
RES["fe_co2_fd"] = {
    "d_renew": [round(float(fdm.params["d_renew"]), 5), round(float(fdm.bse["d_renew"]), 5),
                round(float(fdm.pvalues["d_renew"]), 5), round(float(fdm.tvalues["d_renew"]), 3)],
    "n": int(fdm.nobs),
    "r2": round(float(fdm.rsquared), 3),
    "note": "First-difference within estimator: country-level year-on-year change in ln(CO2/capita) on "
            "year-on-year change in renewable share.",
}

# --------------------------------------------------------------------------- #
# 6c. Mechanism: displacement vs addition, decomposed by region
# --------------------------------------------------------------------------- #
print("Displacement vs addition analysis ...")
g = df.copy()
g["renew_gen"] = g["electricity_generation"] * g["renewables_share_elec"] / 100.0
g["fossil_gen"] = g["electricity_generation"] * g["fossil_share_elec"] / 100.0

world = g.groupby("year")[["renew_gen", "fossil_gen", "electricity_generation"]].sum()
w0, w1 = world.loc[START], world.loc[END]
d_renew_world = float(w1["renew_gen"] - w0["renew_gen"])
d_fossil_world = float(w1["fossil_gen"] - w0["fossil_gen"])
disp_ratio = -d_fossil_world / d_renew_world if d_renew_world > 0 else None
RES["displacement"] = {
    "world_renew_gen_2000": round(float(w0["renew_gen"]), 0),
    "world_renew_gen_end": round(float(w1["renew_gen"]), 0),
    "world_fossil_gen_2000": round(float(w0["fossil_gen"]), 0),
    "world_fossil_gen_end": round(float(w1["fossil_gen"]), 0),
    "delta_renew_world_TWh": round(d_renew_world, 0),
    "delta_fossil_world_TWh": round(d_fossil_world, 0),
    "displacement_ratio": round(float(disp_ratio), 3) if disp_ratio is not None else None,
    "world_total_gen_2000": round(float(w0["electricity_generation"]), 0),
    "world_total_gen_end": round(float(w1["electricity_generation"]), 0),
    "note": "displacement_ratio = -Δfossil_gen / Δrenew_gen. Positive => fossil generation fell as "
            "renewables rose (net displacement). Negative => fossil generation rose alongside renewables (addition).",
}

# per-country 2000->END: classify displacing vs adding (clean frame)
gc = g.pivot_table(index="iso_code", columns="year", values=["renew_gen", "fossil_gen"])
sub = gc.dropna(subset=[("renew_gen", START), ("renew_gen", END), ("fossil_gen", START), ("fossil_gen", END)]).copy()
sub["d_renew"] = sub[("renew_gen", END)] - sub[("renew_gen", START)]
sub["d_fossil"] = sub[("fossil_gen", END)] - sub[("fossil_gen", START)]
sub["displacing"] = sub["d_fossil"] < 0
n_cty = int(len(sub))
n_disp = int(sub["displacing"].sum())

# renewable-share gain and CO2 change per country (for mechanism linkage)
sc = df.pivot_table(index="iso_code", columns="year", values="renewables_share_elec")
sc = sc.dropna(subset=[START, END]); sc["re_gain"] = sc[END] - sc[START]
cc = df.pivot_table(index="iso_code", columns="year", values="co2_per_capita")
cc = cc.dropna(subset=[START, END]); cc["co2_change_pct"] = (cc[END] - cc[START]) / cc[START] * 100

subc = pd.DataFrame({
    "iso_code": sub.index,
    "d_renew": sub["d_renew"].values,
    "d_fossil": sub["d_fossil"].values,
    "displacing": sub["displacing"].values,
})
subc["re_gain"] = subc["iso_code"].map(sc["re_gain"])
subc["co2_change_pct"] = subc["iso_code"].map(cc["co2_change_pct"])
reg_map = df.drop_duplicates("iso_code").set_index("iso_code")["region"]
subc["region"] = subc["iso_code"].map(reg_map)

corr_gain_fossil = float(np.corrcoef(subc["re_gain"], subc["d_fossil"])[0, 1]) if len(subc) > 2 else None
corr_fossil_co2 = float(np.corrcoef(subc["d_fossil"], subc["co2_change_pct"])[0, 1]) if len(subc) > 2 else None
RES["displacement"]["n_countries"] = n_cty
RES["displacement"]["n_displacing"] = n_disp
RES["displacement"]["pct_displacing"] = round(n_disp / n_cty * 100, 1)
RES["displacement"]["corr_renewgain_d_fossil"] = round(corr_gain_fossil, 3) if corr_gain_fossil is not None else None
RES["displacement"]["corr_dfossil_dco2"] = round(corr_fossil_co2, 3) if corr_fossil_co2 is not None else None

# regional decomposition
reg_disp = {}
for rg, gr in subc.groupby("region"):
    dr = -gr["d_fossil"].sum() / gr["d_renew"].sum() if gr["d_renew"].sum() > 0 else None
    reg_disp[rg] = {
        "displacement_ratio": round(float(dr), 3) if dr is not None else None,
        "n_countries": int(len(gr)),
        "n_displacing": int(gr["displacing"].sum()),
        "pct_displacing": round(float(gr["displacing"].mean() * 100), 1),
    }
RES["displacement_regional"] = reg_disp

# --------------------------------------------------------------------------- #
# 6d. Robustness suite
# --------------------------------------------------------------------------- #
print("Robustness checks ...")
rob = {}
# (a) subsample 2010-2022
sub10 = reg_df[reg_df["year"] >= 2010]
m10 = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
              data=sub10).fit(cov_type="HC1")
rob["subsample_2010_2022"] = coef_block(m10, "renewables_share_elec")
# (b) drop top-5% emitters (by mean CO2 per capita)
mean_co2 = reg_df.groupby("iso_code")["co2_per_capita"].mean()
drop_iso = mean_co2.nlargest(int(len(mean_co2) * 0.05)).index
subdrop = reg_df[~reg_df["iso_code"].isin(drop_iso)]
md = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
             data=subdrop).fit(cov_type="HC1")
rob["drop_top5pct_emitters"] = coef_block(md, "renewables_share_elec")
# (c) cluster-robust SE for the baseline (summary)
base_clu = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
                   data=reg_df).fit(cov_type="cluster", cov_kwds={"groups": reg_df["iso_code"]})
rob["baseline_cluster_se"] = round(float(base_clu.bse["renewables_share_elec"]), 5)
# (d) exclude pandemic years 2020-2022 (demand/lockdown shock)
subp = reg_df[reg_df["year"] <= 2019]
mp = smf.ols("log_co2_pc ~ renewables_share_elec + log_gdp_pc + C(iso_code) + C(year_f)",
             data=subp).fit(cov_type="HC1")
rob["exclude_2020_2022"] = coef_block(mp, "renewables_share_elec")
RES["robustness"] = rob

# --------------------------------------------------------------------------- #
# 7. 2030 projection of global renewable share
# --------------------------------------------------------------------------- #
print("2030 projection ...")
ys = ann.index.values.astype(float)
rs = ann["renew_share"].values.astype(float)
mask = ys >= 2013
mfit = sm.OLS(rs[mask], sm.add_constant(ys[mask])).fit()
slope, intercept = float(mfit.params[1]), float(mfit.params[0])
resid_se = float(np.sqrt(mfit.mse_resid))
proj_2030 = slope * 2030 + intercept
band = 1.96 * resid_se
mfit_full = sm.OLS(rs, sm.add_constant(ys)).fit()
proj_2030_full = float(mfit_full.params[1] * 2030 + mfit_full.params[0])
RES["projection_2030"] = {
    "recent_slope_pp_per_yr": round(slope, 3),
    "proj_2030_recent": round(proj_2030, 1),
    "proj_2030_full": round(proj_2030_full, 1),
    "lower_95": round(proj_2030 - band, 1),
    "upper_95": round(proj_2030 + band, 1),
    "fit_window": "2013-2022",
    "note": "Linear extrapolation of the generation-weighted global renewable share. "
            "Assumes momentum of the last decade persists; band = 1.96 x regression residual SE.",
}

# --------------------------------------------------------------------------- #
# 7b. Forward fossil-generation projection + illustrative case studies
# --------------------------------------------------------------------------- #
print("Forward fossil projection + case studies ...")
ys_a = ann.index.values.astype(float)
rs_a = ann["renew_share"].values.astype(float)
lc_a = ann["low_carbon_share"].values.astype(float)
fs_a = ann["fossil_share"].values.astype(float)
tg_a = ann["total_gen"].values.astype(float)
mask = ys_a >= 2013

def _fit(y):
    m = sm.OLS(y[mask], sm.add_constant(ys_a[mask])).fit()
    return float(m.params[1]), float(m.params[0])
rslope, rint = _fit(rs_a)
lslope, lint = _fit(lc_a)
tm = sm.OLS(np.log(tg_a)[mask], sm.add_constant(ys_a[mask])).fit()
tslope, tint = float(tm.params[1]), float(tm.params[0])

fut_years = list(range(int(ys_a[-1]) + 1, 2031))
fp_path = []
for y in fut_years:
    renew = rslope * y + rint
    lowc = lslope * y + lint
    # low-carbon share already includes renewables; fossil is the residual
    fsh = max(0.0, min(100.0, 100 - lowc))
    tot = float(np.exp(tslope * y + tint))
    fp_path.append({"year": y, "renew_share": round(renew, 1),
                    "low_carbon_share": round(lowc, 1), "fossil_share": round(fsh, 1),
                    "total_gen_TWh": round(tot, 0), "fossil_gen_TWh": round(fsh / 100.0 * tot, 0)})
base_fg = float(fs_a[-1] / 100.0 * tg_a[-1])
RES["projection_fossil"] = {
    "base_year": int(ys_a[-1]),
    "base_fossil_gen_TWh": round(base_fg, 0),
    "proj_2030_fossil_gen_TWh": fp_path[-1]["fossil_gen_TWh"],
    "path": fp_path,
    "recent_slope_renew_pp_yr": round(rslope, 3),
    "recent_slope_lowcarbon_pp_yr": round(lslope, 3),
    "recent_growth_total_gen_pct_yr": round((np.exp(tslope) - 1) * 100, 2),
    "note": "Holds the 2013-2022 momentum of renewable share, low-carbon share and total "
            "electricity demand. Fossil generation = remaining share x total generation. "
            "Illustrative, not a supply-side model.",
}

# illustrative case studies (six countries with contrasting stories)
CS_ISO = ["DEU", "DNK", "CHN", "USA", "IND", "GBR"]
cname = df.drop_duplicates("iso_code").set_index("iso_code")["country"]
cregion = df.drop_duplicates("iso_code").set_index("iso_code")["region"]
piv = df[df["iso_code"].isin(CS_ISO)].pivot_table(
    index="year", columns="iso_code",
    values=["renewables_share_elec", "fossil_share_elec"])
subc_idx = subc.set_index("iso_code")
cs_list = []
for iso in CS_ISO:
    if iso not in piv["renewables_share_elec"].columns:
        continue
    rser = piv["renewables_share_elec"][iso]
    fser = piv["fossil_share_elec"][iso]
    yrs = [int(y) for y in rser.index]
    r0 = float(rser.loc[START]); r1 = float(rser.loc[END])
    f0 = float(fser.loc[START]); f1 = float(fser.loc[END])
    co2c = df[df["iso_code"] == iso].set_index("year")["co2_per_capita"]
    c0 = float(co2c.loc[START]); c1 = float(co2c.loc[END])
    in_sub = iso in subc_idx.index
    cs_list.append({
        "iso": iso, "name": str(cname.get(iso, iso)), "region": str(cregion.get(iso, "")),
        "renew_2000": round(r0, 1), "renew_end": round(r1, 1),
        "fossil_2000": round(f0, 1), "fossil_end": round(f1, 1),
        "co2pc_2000": round(c0, 2), "co2pc_end": round(c1, 2),
        "co2_change_pct": round((c1 - c0) / c0 * 100, 1) if c0 > 0 else None,
        "d_renew_TWh": round(float(subc_idx.loc[iso, "d_renew"]), 1) if in_sub else None,
        "d_fossil_TWh": round(float(subc_idx.loc[iso, "d_fossil"]), 1) if in_sub else None,
        "displacing": bool(subc_idx.loc[iso, "displacing"]) if in_sub else None,
        "decoupling": str(d_full.loc[iso, "cat"]) if (iso in d_full.index and "cat" in d_full.columns) else None,
        "years": yrs,
        "renew_series": [None if pd.isna(v) else round(float(v), 1) for v in rser.tolist()],
        "fossil_series": [None if pd.isna(v) else round(float(v), 1) for v in fser.tolist()],
    })
RES["case_studies"] = cs_list
print(f"  case studies: {len(cs_list)} countries")

# --------------------------------------------------------------------------- #
# 7c. What it would take: scenarios for global fossil generation to 2030
# --------------------------------------------------------------------------- #
print("What-it-takes counterfactual ...")
pf = RES["projection_fossil"]
T0 = float(tg_a[-1]); L0 = float(lc_a[-1]); F0 = float(fs_a[-1] / 100.0 * tg_a[-1])
g = pf["recent_growth_total_gen_pct_yr"] / 100.0
T2030 = T0 * (1 + g) ** (2030 - int(ys_a[-1]))
scen = {}
for name, frac in [("flat", 1.0), ("cut10", 0.9), ("cut30", 0.7)]:
    ftarget = F0 * frac
    lneed = 1 - ftarget / T2030
    scen[name] = {"fossil_TWh_2030": round(ftarget, 0),
                  "low_carbon_share_needed_2030": round(lneed * 100, 1),
                  "low_carbon_share_gain_pp": round(lneed * 100 - L0, 1)}
L_momentum = fp_path[-1]["low_carbon_share"]
RES["what_it_takes"] = {
    "base_year": int(ys_a[-1]), "base_total_gen_TWh": round(T0, 0),
    "base_low_carbon_share": round(L0, 1), "base_fossil_gen_TWh": round(F0, 0),
    "demand_growth_pct_yr": round(g * 100, 2), "total_gen_2030_TWh": round(T2030, 0),
    "momentum_low_carbon_2030": L_momentum,
    "scenarios": scen,
    "note": ("Assuming 2022-2030 electricity demand grows at the recent (2013-2022) rate. "
             "Required low-carbon share = 1 - (target fossil TWh) / (projected 2030 total generation). "
             "Compares the policy ask against the constant-momentum trajectory."),
}
print(f"  to hold fossil flat by 2030 need low-carbon share {scen['flat']['low_carbon_share_needed_2030']}% "
      f"(momentum only reaches {L_momentum}%)")

# --------------------------------------------------------------------------- #
# 8. Figures (publication quality: DPI 300, consistent style)
# --------------------------------------------------------------------------- #
print("Figures ...")
plt.rcParams.update({"figure.dpi": 300, "font.size": 11, "font.family": "DejaVu Sans",
                     "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.axisbelow": True})
C = {"renew": "#2ca02c", "fossil": "#d62728", "lowc": "#1f77b4", "ink": "#333333"}

# Fig 1: global trend
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(ann.index, ann["renew_share"], color=C["renew"], lw=2.5, label="Renewables")
ax.plot(ann.index, ann["low_carbon_share"], color=C["lowc"], lw=2.5, ls="--", label="Low-carbon (incl. nuclear)")
ax.plot(ann.index, ann["fossil_share"], color=C["fossil"], lw=2.5, label="Fossil")
ax.set_ylabel("Share of electricity generation (%)")
ax.set_title("Global electricity mix, 2000-2022 (generation-weighted)")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "figure1_global_trend.png"); plt.close(fig)

# Fig 2: regional renewable share
fig, ax = plt.subplots(figsize=(8, 4.5))
cmap = plt.colormaps["tab10"]
for i, r in enumerate(reg.columns):
    ax.plot(reg.index, reg[r], lw=2, color=cmap(i), label=r)
ax.set_ylabel("Renewables share of electricity (%)")
ax.set_title("Renewable electricity share by region, 2000-2022")
ax.legend(frameon=False, ncol=2, fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "figure2_regional.png"); plt.close(fig)

# Fig 3: beta-convergence
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(bdf["x"], bdf["y"] * 100, s=18, alpha=0.6, color=C["renew"])
xs = np.linspace(bdf["x"].min(), bdf["x"].max(), 50)
ax.plot(xs, (beta_mod.params["const"] + beta_mod.params["x"] * xs) * 100, color="black", lw=2)
ax.set_xlabel("Initial renewables share, 2000 (log %)")
ax.set_ylabel("Annual growth rate 2000-2022 (%/yr, log)")
ax.set_title(f"beta-convergence: slope={beta_mod.params['x']:.4f} (p={beta_mod.pvalues['x']:.3f})")
fig.tight_layout(); fig.savefig(FIG / "figure3_beta.png"); plt.close(fig)

# Fig 4: Tapio decoupling bars across windows
fig, axes = plt.subplots(1, len(windows), figsize=(5 * len(windows), 4.3))
cats_order = ["Absolute decoupling", "Relative decoupling", "Coupling", "Expansive coupling", "Recessionary (GDP falling)"]
colors = ["#2ca02c", "#98df8a", "#ff9896", "#d62728", "#bcbcbc"]
for ax, lab in zip(axes, windows.keys()):
    d = RES["tapio"][lab]
    vals = [d["counts"].get(c, 0) for c in cats_order]
    ax.bar(range(len(cats_order)), vals, color=colors)
    ax.set_title(lab, fontsize=10)
    ax.set_xticks(range(len(cats_order)))
    ax.set_xticklabels([c.split(" (")[0].replace(" decoupling", "") for c in cats_order], rotation=35, ha="right", fontsize=7)
    for i, v in enumerate(vals):
        if v: ax.text(i, v + 0.4, str(v), ha="center", fontsize=8)
    ax.set_ylabel("Countries")
fig.suptitle("GDP-CO2 decoupling typology (Tapio) by window", y=1.04, fontsize=11)
fig.tight_layout(); fig.savefig(FIG / "figure4_tapio.png", bbox_inches="tight"); plt.close(fig)

# Fig 5: renewable gain vs decoupling index
fig, ax = plt.subplots(figsize=(7.5, 5))
sc = RES["decouple_scatter"]
dfp = pd.DataFrame({"x": sc["re_gain"], "y": sc["DI"], "c": sc["cat"]})
palette = {"Absolute decoupling": "#2ca02c", "Relative decoupling": "#98df8a",
           "Coupling": "#ff9896", "Expansive coupling": "#d62728", "Recessionary (GDP falling)": "#bcbcbc"}
for c, g_ in dfp.groupby("c"):
    ax.scatter(g_["x"], g_["y"], s=22, alpha=0.7, label=c, color=palette.get(c, "#333"))
ax.axhline(0, color="gray", lw=0.8); ax.axhline(1, color="gray", lw=0.8, ls="--")
ax.set_xlabel(f"Change in renewables share of electricity, 2000-{END} (pp)")
ax.set_ylabel("Tapio decoupling index (CO2 growth / GDP growth)")
ax.set_title(f"Renewable gains vs decoupling (r={RES['tapio'][f'2000-{END}']['corr_renewgain_DI']})")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(FIG / "figure5_renew_decoupling.png"); plt.close(fig)

# Fig 6: decoupling prevalence trend
fig, ax = plt.subplots(figsize=(8, 4.3))
wp = RES["tapio_prevalence"]
wlab = [p["window"] for p in wp]
ax.plot(wlab, [p["pct_absolute"] for p in wp], "-o", color=C["renew"], lw=2, label="Absolute decoupling")
ax.plot(wlab, [p["pct_relative"] for p in wp], "-s", color="#1f77b4", lw=2, label="Relative decoupling")
ax.set_ylabel("% of countries")
ax.set_title("Decoupling prevalence across rolling windows")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "figure6_prevalence.png"); plt.close(fig)

# Fig 7: FE coefficient forest by region
fig, ax = plt.subplots(figsize=(8, 4.5))
het_items = list(RES["fe_co2_heterogeneity"].items())
ylab = [k for k, _ in het_items]
pts = [v["coef"][0] * 100 for k, v in het_items]
errs = [v["coef"][1] * 100 for k, v in het_items]
ypos = range(len(ylab))
ax.errorbar(pts, ypos, xerr=1.96 * np.array(errs), fmt="o", color="#2ca02c", capsize=4)
ax.axvline(0, color="gray", lw=0.8)
ax.set_yticks(list(ypos)); ax.set_yticklabels(ylab)
ax.set_xlabel("% change in CO2/capita per +100 pp renewable share (FE, 95% CI)")
ax.set_title("Heterogeneity: renewable share & CO2/capita by region")
fig.tight_layout(); fig.savefig(FIG / "figure7_heterogeneity.png"); plt.close(fig)

# Fig 8: 2030 projection
fig, ax = plt.subplots(figsize=(8, 4.3))
ax.plot(ys, rs, "-o", color=C["renew"], lw=2, label="Actual 2000-2022")
fx = np.linspace(2013, 2030, 50)
ax.plot(fx, slope * fx + intercept, "--", color="black", lw=2, label="Recent trend fit (2013-22)")
ax.fill_between(fx, (slope * fx + intercept) - band, (slope * fx + intercept) + band, color="gray", alpha=0.2)
ax.scatter([2030], [proj_2030], color="red", zorder=5)
ax.annotate(f"2030 projection:\n{proj_2030:.1f}%  [{RES['projection_2030']['lower_95']:.0f}, {RES['projection_2030']['upper_95']:.0f}]",
            (2030, proj_2030), textcoords="offset points", xytext=(-120, 10), fontsize=9, color="red")
ax.set_ylabel("Renewables share of electricity (%)")
ax.set_xlim(2000, 2032)
ax.set_title("Global renewable electricity share: actual and 2030 projection")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "figure8_projection.png"); plt.close(fig)

# Fig 9: event-study coefficients
fig, ax = plt.subplots(figsize=(8, 4.3))
xs = [i for i, v in enumerate(es_coef) if v is not None]
ys_c = [es_coef[i] for i in xs]
err = [es_ci[i] for i in xs]
ax.errorbar([rel_years[i] for i in xs], ys_c, yerr=err, fmt="o-", color="#1b6b3a", capsize=3, lw=1.5)
ax.axhline(0, color="gray", lw=0.8)
ax.axvline(-0.5, color="gray", lw=0.8, ls=":")
ax.set_xlabel("Years relative to renewable buildout event (crossing 25%)")
ax.set_ylabel("% deviation in CO2/capita vs year -1")
ax.set_title(f"Event study: emissions trajectory around renewable buildout (n={RES['event_study']['n_countries']} countries)")
fig.tight_layout(); fig.savefig(FIG / "figure9_event_study.png"); plt.close(fig)

# Fig 10: per-country displacement scatter
fig, ax = plt.subplots(figsize=(7.5, 5))
ax.scatter(sub["d_renew"] / 1000, sub["d_fossil"] / 1000, s=20, alpha=0.6, color="#1b6b3a")
lim = max(sub["d_renew"].max(), sub["d_fossil"].max()) / 1000
ax.plot([0, lim], [0, lim], color="gray", ls=":", lw=1, label="Pure addition (1:1)")
ax.axhline(0, color="#d62728", lw=1, ls="--")
ax.set_xlabel("Change in renewable generation 2000-2022 (TWh)")
ax.set_ylabel("Change in fossil generation 2000-2022 (TWh)")
ax.set_title(f"Displacing or adding? {n_disp}/{n_cty} countries cut fossil generation")
ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "figure10_displacement.png"); plt.close(fig)

# Fig 11: regional displacement decomposition
fig, ax = plt.subplots(figsize=(8, 4.3))
rgs = list(reg_disp.keys())
ratios = [reg_disp[r]["displacement_ratio"] for r in rgs]
pcts = [reg_disp[r]["pct_displacing"] for r in rgs]
xpos = np.arange(len(rgs))
ax.bar(xpos - 0.2, ratios, width=0.4, color="#1b6b3a", label="Displacement ratio (-Δfossil/Δrenew)")
ax.bar(xpos + 0.2, [p / 100 for p in pcts], width=0.4, color="#1f77b4", label="% countries cutting fossil")
ax.axhline(0, color="gray", lw=0.8)
ax.set_xticks(xpos); ax.set_xticklabels(rgs)
ax.set_ylabel("Displacement ratio  /  share cutting fossil")
ax.set_title("Displacement vs addition, by region (2000-2022)")
ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "figure11_displacement_regional.png"); plt.close(fig)

# Fig 12: carbon intensity of electricity vs renewable share (deciles)
fig, ax = plt.subplots(figsize=(8, 4.3))
ci_all = df.dropna(subset=["carbon_intensity_elec", "renewables_share_elec"]).copy()
ci_all = ci_all[ci_all["carbon_intensity_elec"] > 0]
bins = np.quantile(ci_all["renewables_share_elec"], np.linspace(0, 1, 11))
ci_all["bin"] = pd.cut(ci_all["renewables_share_elec"], bins, include_lowest=True, duplicates="drop")
centers = ci_all.groupby("bin", observed=True)["renewables_share_elec"].mean().values
means = ci_all.groupby("bin", observed=True)["carbon_intensity_elec"].mean().values
ax.plot(centers, means, "-o", color="#1b6b3a", lw=2)
ax.set_xlabel("Renewables share of electricity (% , decile bins)")
ax.set_ylabel("Mean CO2 intensity of electricity (gCO2/kWh)")
ax.set_title("Grid carbon intensity falls monotonically with renewable share")
fig.tight_layout(); fig.savefig(FIG / "figure12_carbon_intensity.png"); plt.close(fig)

# Fig 13: case-study small multiples
fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, cs in zip(axes.flat, RES["case_studies"]):
    ax.plot(cs["years"], cs["renew_series"], color=C["renew"], lw=2, label="Renewables")
    ax.plot(cs["years"], cs["fossil_series"], color=C["fossil"], lw=2, label="Fossil")
    ax.set_ylim(0, 100); ax.grid(True, alpha=0.3)
    ax.set_title(f"{cs['name']}  ({cs['renew_2000']:.0f}%→{cs['renew_end']:.0f}%)", fontsize=10)
    ax.set_xlabel("Year")
fig.legend(["Renewables", "Fossil"], loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Six illustrative country trajectories, 2000-2022", y=1.02, fontsize=12)
fig.tight_layout(); fig.savefig(FIG / "figure13_case_studies.png", bbox_inches="tight"); plt.close(fig)

# Fig 14: forward fossil generation (actual + projected)
fa_years = ann.index.tolist()
fa_vals = [round(float(ann["fossil_share"].loc[y]) / 100.0 * float(ann["total_gen"].loc[y]), 0) for y in fa_years]
fy = [p["year"] for p in fp_path]
fv = [p["fossil_gen_TWh"] for p in fp_path]
fig, ax = plt.subplots(figsize=(8, 4.3))
ax.plot(fa_years, fa_vals, color=C["fossil"], lw=2.5, label="Actual")
ax.plot(fy, fv, color=C["fossil"], lw=2.5, ls="--", label="Projected (constant momentum)")
ax.axvline(END, color="gray", ls=":", lw=1)
ax.set_ylabel("Fossil generation (TWh)")
ax.set_xlim(2000, 2032)
ax.annotate(f"2030 \u2248 {fp_path[-1]['fossil_gen_TWh']:,.0f} TWh", (2030, fp_path[-1]["fossil_gen_TWh"]),
            textcoords="offset points", xytext=(-135, 8), fontsize=9, color=C["fossil"])
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "figure14_forward_fossil.png"); plt.close(fig)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# 8.5 Per-country panel for the interactive explorer
# --------------------------------------------------------------------------- #
print("Country panel for explorer ...")
name_map = df.drop_duplicates("iso_code").set_index("iso_code")["country"]
dfull_cat = d_full["cat"].to_dict() if "cat" in d_full else {}
sh = df.pivot_table(index="iso_code", columns="year",
                    values=["renewables_share_elec", "fossil_share_elec", "co2_per_capita"])
yr = list(range(START, END + 1))
subc_idx = subc.set_index("iso_code")
cp = []
for iso in subc_idx.index:
    r0 = sh.loc[iso, ("renewables_share_elec", START)]
    r1 = sh.loc[iso, ("renewables_share_elec", END)]
    f0 = sh.loc[iso, ("fossil_share_elec", START)]
    f1 = sh.loc[iso, ("fossil_share_elec", END)]
    c0 = sh.loc[iso, ("co2_per_capita", START)]
    c1 = sh.loc[iso, ("co2_per_capita", END)]
    rser = [None if pd.isna(sh.loc[iso, ("renewables_share_elec", y)]) else round(float(sh.loc[iso, ("renewables_share_elec", y)]), 1) for y in yr]
    fser = [None if pd.isna(sh.loc[iso, ("fossil_share_elec", y)]) else round(float(sh.loc[iso, ("fossil_share_elec", y)]), 1) for y in yr]
    cp.append({
        "iso": iso,
        "name": str(name_map.get(iso, iso)),
        "region": str(subc_idx.loc[iso, "region"]),
        "renew_2000": None if pd.isna(r0) else round(float(r0), 1),
        "renew_end": None if pd.isna(r1) else round(float(r1), 1),
        "fossil_2000": None if pd.isna(f0) else round(float(f0), 1),
        "fossil_end": None if pd.isna(f1) else round(float(f1), 1),
        "co2pc_2000": None if pd.isna(c0) else round(float(c0), 2),
        "co2pc_end": None if pd.isna(c1) else round(float(c1), 2),
        "d_renew_TWh": round(float(subc_idx.loc[iso, "d_renew"]), 1),
        "d_fossil_TWh": round(float(subc_idx.loc[iso, "d_fossil"]), 1),
        "displacing": bool(subc_idx.loc[iso, "displacing"]),
        "decoupling": dfull_cat.get(iso),
        "renew_series": rser,
        "fossil_series": fser,
    })
RES["country_panel"] = cp
print(f"  country-panel rows: {len(cp)}")

# 9. Save
# --------------------------------------------------------------------------- #
with open(ROOT / "results.json", "w") as f:
    json.dump(RES, f, indent=2, default=str)
print("\n=== KEY RESULTS ===")
print(json.dumps({
    "desc_stats_overall": RES["desc_stats"]["overall"],
    "fe_table": RES["fe_table"]["rows"],
    "fe_f_test": RES["fe_f_test"],
    "fe_carbon_intensity": RES["fe_carbon_intensity"],
    "robustness": RES["robustness"],
    "displacement_regional": RES["displacement_regional"],
}, indent=2, default=str))
print("\nSaved results.json and 12 figures.")
