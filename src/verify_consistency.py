"""Consistency check: do report.html and manuscript.tex agree with results.json?

Catches the single biggest risk in a data-driven paper -- prose/table numbers
drifting away from the computed results. Run:  python src/verify_consistency.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
R = json.load(open(ROOT / "results.json"))
report = (ROOT / "report.html").read_text(encoding="utf-8")
manuscript = (ROOT / "manuscript.tex").read_text(encoding="utf-8")
index = (ROOT / "index.html").read_text(encoding="utf-8")


def pct_pp(d):
    return d["coef"][0] * 100


checks = []

# --- heterogeneity by region (from results.json) ---
het = R["fe_co2_heterogeneity"]
for rg in ["America", "Europe", "Asia", "Africa"]:
    v = het[rg]
    needle = f"{pct_pp(v):.2f}%/pp"
    checks.append((f"report het {rg} = {needle}", needle in report))

# --- FE baseline in manuscript ---
fe = R["fe_co2"]["contemporaneous"]["coef"][0]
checks.append((f"manuscript FE coef = {fe:.4f}", f"{fe:.4f}" in manuscript))

# --- F-test ---
ft = R["fe_f_test"]["F"]
checks.append((f"manuscript F-test = {ft:.1f}", f"{ft:.1f}" in manuscript))

# --- displacement ---
disp = R["displacement"]
checks.append((f"report fossil added = {disp['delta_fossil_world_TWh']:,.0f} TWh",
               f"{disp['delta_fossil_world_TWh']:,.0f}" in report))
checks.append((f"manuscript fossil added = {disp['delta_fossil_world_TWh']:,.0f} TWh",
               f"{disp['delta_fossil_world_TWh']:,.0f}" in manuscript))
checks.append((f"report pct displacing = {disp['pct_displacing']:.0f}%",
               f"{disp['pct_displacing']:.0f}%" in report))

# --- tercile (manuscript Table 5) ---
tert = R["fe_co2_tercile"]
checks.append((f"manuscript tercile low = {pct_pp(tert['groups']['Low']):.2f}",
               f"{pct_pp(tert['groups']['Low']):.2f}" in manuscript))
checks.append((f"manuscript tercile high = {pct_pp(tert['groups']['High']):.2f}",
               f"{pct_pp(tert['groups']['High']):.2f}" in manuscript))

# --- dashboard contains the country panel ---
dash = (ROOT / "dashboard.html").read_text(encoding="utf-8")
checks.append(("dashboard has country panel", '"country_panel"' in dash))

# --- landing page (index.html) ---
if (ROOT / "index.html").exists():
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    checks.append((f"index fossil added = {disp['delta_fossil_world_TWh']:,.0f} TWh",
                   f"{disp['delta_fossil_world_TWh']:,.0f}" in idx))
    checks.append((f"index pct displacing = {disp['pct_displacing']:.0f}%",
                   f"{disp['pct_displacing']:.0f}%" in idx))
    checks.append(("index has #utility section", 'id="utility"' in idx))
    checks.append(("index has #howto section", 'id="howto"' in idx))
    checks.append(("index has JSON-LD", "application/ld+json" in idx))
    checks.append(("index has OG/Twitter cards", 'property="og:title"' in idx and "twitter:card" in idx))
    checks.append(("index links dashboard/report/pdf/data",
                   'href="dashboard.html"' in idx and 'href="report.html"' in idx
                   and 'href="manuscript.pdf"' in idx and 'href="results.json"' in idx))
    # --- new research outputs (forward projection + case studies) ---
    pf = R["projection_fossil"]
    checks.append(("results has projection_fossil", "projection_fossil" in R))
    checks.append((f"index forward fossil 2030 = {pf['proj_2030_fossil_gen_TWh']:,.0f} TWh",
                   f"{pf['proj_2030_fossil_gen_TWh']:,.0f}" in idx))
    checks.append(("index has #explore (interactive chart)", 'id="explore"' in idx))
    checks.append(("index has #faq (myth vs fact)", 'id="faq"' in idx))
    checks.append(("index has #stories (case studies)", 'id="stories"' in idx))
    checks.append(("results has case_studies with displacing flag",
                   len(R.get("case_studies", [])) >= 6
                   and all(c.get("displacing") is not None for c in R["case_studies"])))

# --- dashboard enhancements ---
checks.append(("dashboard has forward projection chart", 'id="fig8b"' in dash))
checks.append(("dashboard has case-study quick links", 'id="cstories"' in dash))

# --- what_it_takes counterfactual ---
wit = R["what_it_takes"]
checks.append(("results has what_it_takes", "what_it_takes" in R))
checks.append((f"report flat-fossil need = {wit['scenarios']['flat']['low_carbon_share_needed_2030']:.1f}%",
               f"{wit['scenarios']['flat']['low_carbon_share_needed_2030']:.1f}" in report))
checks.append(("report 4.11 what-it-takes section", "What it would take" in report))
checks.append(("dashboard what-it-takes callout", "What it would take instead" in dash))
checks.append(("dashboard placeholders replaced", "__FLAT__" not in dash and "__GAP__" not in dash))

# --- artifact existence ---
for f in ["figures/figure13_case_studies.png", "figures/figure14_forward_fossil.png", "sitemap.xml",
          "robots.txt", "post_zh.md", "post_en.md", "sources/LITERATURE.md", "sources/manifest.json",
          "figures/hero.png", "figures/social.png", "LICENSE", "CITATION.cff", "README.md",
          ".zenodo.json", "index_zh.html"]:
    checks.append((f"file exists: {f}", (ROOT / f).exists()))

# --- no leftover placeholders in published HTML ---
checks.append(("landing has no [user]/[repo] placeholder", "[user]" not in index and "[repo]" not in index))
checks.append(("landing has no [Your Name] placeholder", "[Your Name]" not in index))
checks.append(("dashboard compare section present", "Compare two countries" in dash))
checks.append(("dashboard compare controls present", 'id="cmpA"' in dash and 'id="cmpB"' in dash))
checks.append(("dashboard og:image is social.png", "figures/social.png" in dash))

ok = all(v for _, v in checks)
for name, passed in checks:
    print(("PASS " if passed else "FAIL ") + name)
print("\nALL CONSISTENT" if ok else "\n*** INCONSISTENCY DETECTED ***")
raise SystemExit(0 if ok else 1)
