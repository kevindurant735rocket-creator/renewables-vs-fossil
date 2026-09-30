# Did renewables displace fossil power?

**A reproducible 163-country test of whether renewables retire fossil generation.**

The renewables build-out is not in doubt. Whether it *displaces* fossil — or merely
accompanies a still-growing electricity system — is a different question, and the answer
here is uncomfortable: **both happened, and fossil won the terawatt-hour race.**

> **163 countries · 3,749 country-years · 2000–2022**
> Renewables added **5,636 TWh**. Fossil added **7,861 TWh**.
> Only **51 of 163 countries (31%)** cut fossil generation at all.

## The headline: addition, not substitution

| | 2000 | 2022 | change |
|---|---|---|---|
| renewable share of generation | 18.73% | 29.45% | **+10.72 pp** |
| fossil share of generation | 64.58% | 61.39% | −3.19 pp |
| world renewable generation | 2,852 TWh | 8,487 TWh | **+5,636 TWh** |
| world fossil generation | 9,833 TWh | **17,693 TWh** | **+7,861 TWh** |
| world total generation | 15,225 TWh | 28,820 TWh | +13,595 TWh |

The renewable share fell by 3 points and total generation nearly doubled. So fossil's
*share* went down while its *volume* went up 80%. The displacement ratio — minus Δfossil
over Δrenewables — is **−1.40**. Negative means addition.

**The sharpest single number:** the correlation between a country's renewable-share gain
and its change in fossil generation is **0.002**. Essentially zero. Countries that built
the most wind and solar were not the countries that closed the most coal plants.

Where displacement does happen, it is regional and stark:

| region | countries | that cut fossil | displacement ratio |
|---|---|---|---|
| Europe | 38 | 27 (**71%**) | +0.34 |
| Oceania | 2 | 2 (100%) | +0.24 |
| America | 27 | 8 (30%) | −0.05 |
| Africa | 50 | 8 (16%) | −2.54 |
| Asia | 46 | 6 (**13%**) | −2.29 |

Europe displaced. Asia and Africa added, and Asia has the largest absolute fossil
build-out in the world. Africa's ratio of −2.54 means fossil generation grew more than
2.5× as fast as renewables.

## The mechanism is real, even if the volume is not

Fixed-effects panel, dependent variable ln(CO₂ per capita), country + year effects:

| specification | coefficient on renewable share | n | R² |
|---|---|---|---|
| contemporaneous | **−0.607%/pp** | 3,749 | 0.984 |
| lagged one year | −0.513%/pp | 3,586 | 0.984 |
| drop top 5% emitters | −0.601%/pp | 3,565 | 0.982 |
| exclude 2020–2022 | −0.517%/pp | 3,260 | 0.987 |
| 2010–2022 subsample | −0.858%/pp | 2,119 | 0.991 |

Country fixed effects are jointly significant (F = 148.06, df 162/3562, p < 0.001),
rejecting pooled OLS. An independent outcome confirms the mechanism more directly: **+1 pp
of renewable share implies 2.2% lower grid carbon intensity** (n = 3,728, R² = 0.966).
If renewables were merely crowding out nuclear or hydro rather than coal and gas, that
intensity coefficient would not hold.

The effect is **larger where decarbonisation is harder** — which is the opposite of what
"easy wins" would predict:

| tercile by 2000 renewable share | effect |
|---|---|
| Low (≤ 6.5%) | −0.23%/pp (p = 0.15, not significant) |
| Mid | −0.45%/pp (p < 0.001) |
| High (≥ 48.8%) | **−0.66%/pp** (p < 0.001) |

By region: America −0.76%/pp, Europe −0.53%/pp, Asia −0.19%/pp (p = 0.46), Africa
−0.12%/pp (p = 0.085). **The clean-energy effect is statistically absent in Asia and
Africa** — which is exactly where fossil generation grew most.

## Decoupling is improving — from a low base

Tapio decoupling classification, 163 countries, 2000–2022:

| | 2000–2005 | 2010–2015 | 2017–2022 |
|---|---|---|---|
| absolute decoupling | 11.0% | 32.5% | **33.7%** |
| relative decoupling | 54.6% | 28.2% | 16.6% |

Countries that started lowest grew fastest (β = −0.024, p < 0.001, n = 137, R² = 0.554)
— genuine convergence. Full-period split: 42 countries absolute (25.8%), 63 relative
(38.7%), 27 expansive coupling, 25 coupling, 6 recessionary.

An event study on the 20 countries crossing a 25% renewable-share threshold (235
observations) estimates a **−10.8%** deviation in ln(CO₂/capita) post-event, at
**p = 0.058** — suggestive, not significant. It is reported here at its real strength.

## The arithmetic to 2030

Holding the 2013–2022 momentum (renewables +0.87 pp/yr, low-carbon +0.74 pp/yr,
generation +2.48%/yr):

| | 2030 |
|---|---|
| renewable share | 36.0% (95% band 35.2–36.8%) |
| low-carbon share | 44.5% |
| **fossil generation** | **19,345 TWh** — up from 17,693 |

Even on its own current trajectory, fossil generation keeps rising through 2030. To hold
fossil flat at the 2022 level, low-carbon share must reach **49.5%**, not 44.5% — a
10.9-point gap. Cut fossil 10% and the requirement is 54.6%; cut 30% and it is 64.7%.

## Reproduce

```bash
git clone https://github.com/kevindurant735rocket-creator/renewables-vs-fossil
cd renewables-vs-fossil

pip install pandas numpy statsmodels scipy   # + weasyprint/pandoc for the PDF

python src/fetch_data.py          # downloads OWID energy + CO2 CSVs into data/
python src/analysis.py            # -> results.json + 14 figures
python src/build_report.py        # -> report.html
python src/build_dashboard.py     # -> dashboard.html (interactive)
python src/build_landing.py       # -> index.html
python src/build_manuscript.py    # -> manuscript.pdf
```

`data/*.csv` is git-ignored on purpose — it is ~100 MB and regenerable from the network.
Every number on every page comes from `results.json`, which `src/analysis.py` computes
from those CSVs. Provenance for each claim is in `sources/manifest.json`.

**The consistency checker needs no data and no network** — it runs on the committed
outputs:

```console
$ python src/verify_consistency.py

PASS report het America = -0.76%/pp
PASS report het Europe = -0.53%/pp
PASS report het Asia = -0.19%/pp
PASS report het Africa = -0.12%/pp
PASS manuscript FE coef = -0.0061
PASS manuscript F-test = 148.1
PASS report fossil added = 7,861 TWh
PASS manuscript fossil added = 7,861 TWh
PASS report pct displacing = 31%
PASS manuscript tercile low = -0.23
PASS manuscript tercile high = -0.66
PASS dashboard has country panel
PASS index fossil added = 7,861 TWh
PASS index pct displacing = 31%
... (52 checks total) ...

ALL CONSISTENT
```

52 checks, 0 failures. It asserts that the HTML report, the manuscript, the dashboard,
the landing page and `results.json` all state the same figures — so a number cannot drift
in one artifact without the checker going red.

## What this is not

- **This is not a causal claim.** Fixed effects, lagging, clustering and
  first-differencing strengthen the association; they do not eliminate confounding. A
  country that decarbonises for unrelated policy reasons also invests in renewables, and
  the model would credit the renewable share for the emissions fall.
- **Electricity only — roughly half of final energy.** Transport, heating and industry
  are out of scope. Conclusions do not transfer to total energy emissions.
- **Electricity-embedded emissions ignore traded-goods carbon leakage.** A country can
  show absolute decoupling partly because production moved offshore.
- **The grid carbon-intensity result is the cleanest mechanism test but still cannot
  distinguish retiring a coal plant from merely changing dispatch order.** That needs
  unit-level data this project does not have.
- **The 2030 number is a constant-momentum extrapolation, not a forecast.** It holds the
  last decade's slopes fixed and models no policy response, price change, supply-side
  constraint or demand elasticity. Read it as a floor under current behaviour.
- **The event study is marginal at p = 0.058.** It does not clear conventional
  significance and is not used to carry any conclusion here.
- **"Only 31% displaced" is a per-country threshold.** A country counts as displacing if
  its fossil generation fell over the window. Countries with flat fossil while renewables
  doubled are counted as non-displacing, which is the honest reading of the underlying
  arithmetic but not the only defensible one.
- **163 countries, not every country.** Sovereign states with complete OWID coverage for
  the required variables in 2000–2022. Small states and territories are absent.
- **It does not argue against renewables.** Every mechanism here points the same way:
  renewables reduce emissions. The finding is that building them has so far mostly
  accompanied demand growth rather than retiring carbon — which is an argument for
  displacement mechanisms, not an argument against the build-out.
- **OWID revises its data.** Country-year values shift as upstream methods improve.

## Make it citable

Before publishing a derivative work:

1. Replace the placeholders in `src/build_landing.py` / `src/build_report.py`
   (`your-github-username`, `renewables-vs-fossil`, `"Your Name"`), and the ORCID in
   `CITATION.cff` / `.zenodo.json`.
2. Archive a release on Zenodo and paste the minted DOI into both files. GitHub + Zenodo
   integration issues a DOI per release tag.

## Layout

```
src/                 fetch_data · analysis · 4 page builders · verify_consistency
data/                raw OWID CSVs (git-ignored, regenerate with fetch_data.py) + CODEBOOK.md
results.json         single source of truth for every published number
figures/             14 publication-quality figures (DPI 300) + hero/social cards
sources/             LITERATURE.md + manifest.json (evidence traceability)
report.html          the full written report
dashboard.html       interactive explorer, per-country panel
manuscript.tex/.pdf  academic manuscript (12 references)
policy_brief.html    short policy-facing brief
index.html           landing page (EN) · index_zh.html (中文)
preprint.md          Markdown version of the manuscript
post_en.md           plain-language read · post_zh.md  中文版
CITATION.cff         citation metadata (GitHub renders it)
.zenodo.json         Zenodo deposit metadata
```

## Data and license

- **Data:** Our World in Data energy and CO₂ datasets —
  [ourworldindata.org/energy-data](https://ourworldindata.org/energy-data), **CC-BY-4.0**,
  used and adapted with attribution.
- **This repository** — analysis code, figures, manuscript and written text —
  **CC-BY-4.0**. See [`LICENSE`](LICENSE). (This project is CC-BY rather than CC-BY-4.0 so the
  figures and manuscript stay shareable and remixable with attribution.)
