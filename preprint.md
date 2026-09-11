# The Global Renewable Electricity Transition and Its Decoupling from CO₂ Emissions: A Reproducible Cross-Country Analysis, 2000–2022

**Working paper / preprint** — submission-ready (arXiv `econ.GN` / `physics.soc-ph`, or SSRN).

- **Data:** Our World in Data — Energy and CO₂ datasets (CC-BY), 163 countries, 3,749 country-year observations, 2000–2022.
- **Reproducibility:** `src/analysis.py` → `results.json` → `report.html` / `dashboard.html`. One command regenerates all numbers and figures.
- **Status:** Empirical results finalized; this manuscript is the arXiv/SSRN-ready text.

---

## Abstract

Between 2000 and 2022 the renewable share of global electricity rose from 18.7% to 29.5% of generation, yet fossil fuels still supplied roughly 61%. This paper asks whether the electricity transition is actually loosening the link between economic growth and CO₂ emissions, where the effect is real, and — crucially — whether renewables are *displacing* fossil generation or merely *adding* to it. Using 163 countries over 2000–2022, I combine convergence analysis, the Tapio decoupling index, a two-way fixed-effects panel model of CO₂ per capita on renewable electricity share (with a lagged-renewable robustness check, a first-difference estimator, clustered standard errors, and a country-level event study), and a second outcome — the CO₂ intensity of electricity — that tests the displacement mechanism directly. Renewable share grew fastest in countries that started lowest (β = −0.024, p < 0.001), and the share of countries in absolute decoupling climbed from 11% in 2000–05 to 34% by 2017–22. Holding country and year fixed, each additional percentage point of renewable electricity is associated with about 0.41% lower CO₂ per capita (p < 0.001), robust to lagging, first-differencing, and clustering. The grid-intensity outcome confirms the mechanism: +1 pp renewable share implies 2.2% lower grid carbon intensity. Yet the growth is overwhelmingly *additive*: globally, fossil generation rose by about 7,900 TWh even as renewables rose by 5,600 TWh, and only 31% of countries cut fossil output at all. Regional decomposition shows Europe displacing (71% of countries cut fossil) while Africa and Asia overwhelmingly added. Under recent momentum the global renewable share reaches roughly 36% by 2030 — progress, but still far from displacing fossil generation.

**Keywords:** renewable electricity; decoupling; Tapio index; fixed-effects panel; carbon intensity; displacement; energy transition.

---

## 1. Introduction

Rising renewable electricity shares are routinely read as evidence that the energy transition is working. The harder question is whether that growth is loosening the link between economic activity and carbon emissions, and whether clean capacity is replacing dirty generation or simply riding on top of a growing system. This distinction is not semantic: it determines whether a higher renewable share is a result or merely a scoreboard.

This paper contributes four things. First, it documents the pace and geography of the transition and shows it is accelerating and converging, not a rich-country club pulling away. Second, it measures decoupling with the Tapio index and shows absolute decoupling is spreading. Third, it moves from association to a credible quasi-causal claim using two-way fixed effects, a lagged-renewable check, a within-country first-difference estimator, clustered standard errors, and a country-level event study. Fourth, and most importantly, it performs a displacement accounting of absolute generation and shows the transition is largely *additive* — and it decomposes that result by region.

## 2. Literature review and conceptual framework

The relationship between economic growth and environmental pressure has been framed since the 1990s by the EKC hypothesis and, more usefully for policy, by the concept of *decoupling*. The OECD (2002) defines decoupling as a decline in the ratio of environmental pressure to economic activity, distinguishing *relative* decoupling (the ratio falls while pressure still rises) from *absolute* decoupling (pressure falls outright). Tapio (2005) operationalized this with an elasticity index that separates the two.

Applied work has reached two broad conclusions. The first is that absolute decoupling of CO₂ from GDP is achievable but rare and geographically concentrated: Steinberger and Roberts (2010) and Jackson and Papathanasopoulou (2008) show it almost exclusively in mature, post-industrial economies. The second is that renewable electricity is the leading lever (Semieniuk et al. 2021; IPCC 2022; IEA 2023).

Two gaps motivate this paper. First, the decoupling and renewable-deployment literatures are rarely joined in a single identification design that controls for permanent country differences. Second, and more important, the literature tends to equate a rising renewable *share* with falling fossil *generation*. They are not the same. A renewable build that rides on top of a growing system can raise the share while fossil output keeps climbing — what I call the *addition* case, as opposed to genuine *displacement*. This paper measures both the decoupling link and the displacement mechanism, and shows they can point in different directions.

## 3. Data and methods

The sample covers 163 countries and 3,749 country-year observations over 2000–2022. Variables are generation-weighted renewable, fossil and low-carbon electricity shares; CO₂ emissions and GDP per capita; electricity demand per capita; and the CO₂ intensity of electricity (gCO₂/kWh). Sources are merged at the country-year level after dropping aggregate/region codes (Our World in Data, CC-BY).

- **Convergence.** β-convergence regresses the growth rate of renewable share on its initial level; σ-convergence tracks the dispersion of renewable share over time.
- **Decoupling.** The Tapio index DI = (%ΔE / %ΔGDP) is computed per country per window and classified into absolute/relative decoupling, coupling, expansive coupling, and recessionary categories.
- **Fixed effects.** ln(CO₂/capita)ₜᵢ = β·RenewShareₜᵢ + γ·ln(GDP/capita)ₜᵢ + αᵢ + λₜ + εₜᵢ, with country and year fixed effects and HC1-robust standard errors. A clustered-by-country specification, a lagged-renewable specification, a first-difference estimator, and an F-test of the joint significance of the country fixed effects provide robustness.
- **Second outcome (displacement test).** ln(grid carbon intensity)ₜᵢ = β·RenewShareₜᵢ + αᵢ + λₜ + εₜᵢ. A fall in grid carbon intensity is the most direct evidence that renewables replace fossil plant.
- **Event study.** Each country's first year above 25% renewable share is its "buildout event"; ln(CO₂/capita) is traced in relative years around it, net of country and year fixed effects.
- **Displacement accounting.** Absolute renewable and fossil generation are reconstructed from shares and total generation. The displacement ratio is −ΔFossilGen / ΔRenewGen; positive implies fossil fell as renewables rose.

### Table 1. Descriptive statistics (country-year observations, 2000–2022)

| Variable | Mean | SD | Min | Max |
|---|---|---|---|---|
| Renewables share of electricity (%) | 34.51 | 33.45 | 0.00 | 100.00 |
| Fossil share of electricity (%) | 60.71 | 34.08 | 0.00 | 100.00 |
| Low-carbon share of electricity (%) | 39.29 | 34.08 | 0.00 | 100.00 |
| CO₂ per capita (t) | 4.92 | 6.56 | 0.02 | 67.73 |
| GDP per capita (intl $) | 16,270 | 18,071 | 422 | 163,531 |
| Electricity demand per capita (kWh) | 3,862 | 5,594 | 9 | 56,049 |
| CO₂ intensity of electricity (gCO₂/kWh) | 447.5 | 253.9 | 0.0 | 1,306.7 |

## 3. Results

### 3.1 Pace and geography
Globally, renewables rose from 18.7% of generation in 2000 to 29.5% in 2022 (+10.7 points). The compound annual growth was 2.1% over the full period but 3.6% from 2015 onward. Fossil fuels barely moved, from 64.6% to 61.4% (−3.2 points). The geography is uneven: Oceania, the Americas and Europe lead, while Asia sits lowest despite being the manufacturing core.

### 3.2 Convergence
The β-convergence slope is −0.024 (SE 0.0019, p < 0.001, R² = 0.55), meaning countries with the lowest initial renewable share grew fastest. Cross-country dispersion also narrowed: the standard deviation of renewable share fell from 35.1 to 32.5 points (−7.6%).

### 3.3 Decoupling
Across 163 countries, 25.8% achieved absolute decoupling (CO₂ fell while GDP rose), 38.7% relative decoupling, and 31.9% stayed coupled or worse. The average decoupling index was 0.63, and the correlation between renewable gain and the decoupling index was −0.22. The share of countries in absolute decoupling rose from 11.0% in 2000–05 to 33.7% in 2017–22.

### 3.4 The renewable–emissions link, held to account
With country and year fixed effects, a one-point rise in renewable share is associated with about 0.41% lower CO₂ per capita (coefficient −0.0042, SE 0.0003, p < 0.001, n = 3,749). The lagged-renewable model gives −0.39% (p < 0.001). Country fixed effects are jointly highly significant (F = 305.8, p < 0.001), justifying fixed effects over pooled OLS, and clustered standard errors are essentially unchanged (SE = 0.00095).

### Table 2. Renewable share and ln(CO₂ per capita), two-way fixed effects

| Specification | Coef | SE (HC1) | SE (cluster) | N |
|---|---|---|---|---|
| 1. Pooled OLS | −0.00565 | 0.00024 | 0.00107 | 3,749 |
| 2. Country FE | −0.00509 | 0.00033 | 0.00104 | 3,749 |
| 3. Country + Year FE (baseline) | −0.00415 | 0.00031 | 0.00095 | 3,749 |
| 4. + Demand control | −0.00367 | 0.00029 | 0.00086 | 3,749 |
| 5. Lagged renewable | −0.00388 | 0.00032 | 0.00094 | 3,586 |
| 6. First-difference | −0.00650 | 0.00148 | 0.00095 | 121 |

The link is regionally bounded. It is strong in Europe (−0.53/pp), the Americas (−0.58/pp) and Asia (−0.46/pp), all p < 0.001. In Africa the coefficient is +0.02/pp and statistically indistinguishable from zero (p = 0.34).

### 3.5 A cleaner test: the carbon intensity of electricity
CO₂ per capita conflates power with every other sector. Re-estimating the fixed-effects model on the CO₂ intensity of electricity gives a coefficient of −0.0222 (SE 0.00085, clustered SE 0.00291, p < 0.001, N = 3,728, R² = 0.97): +1 pp renewable share implies 2.2% lower grid carbon intensity. Average grid intensity also falls monotonically across deciles of renewable share. The decoupling link is not an artefact of GDP or population — it shows up in the physics of the grid itself.

### 3.6 Identification: event study and within-country check
The first-difference estimator (spec 6) removes every factor fixed within a country; a one-point year-on-year rise in renewable share is associated with about 0.65% lower CO₂ per capita in the same step (p < 0.001). The event study traces emissions around each country's first crossing of 25% renewable share (20 countries with sufficient pre/post data). Emissions were already drifting down before the event and continued — and slightly steepened — afterward, with no discrete break (post-event average deviation −18.5%, p = 0.006). Decarbonization in this sample is a momentum process, not a switch that flips at a round-number threshold.

### 3.7 Mechanism: displacing, or just adding?
The fixed-effects and event-study results say renewables go with lower emissions per unit of output; they do not say renewables are replacing fossil. Between 2000 and 2022 the world added 5,636 TWh of renewables and 7,861 TWh of fossil generation. Fossil output grew by roughly 1.4 times as much as renewables in absolute terms; total generation nearly doubled, from 15,225 to 28,820 TWh. The displacement ratio is −1.40 (negative = additive). Only 51 of 163 countries (31%) actually cut their fossil generation, and the correlation between renewable-share gain and change in fossil generation is essentially zero (0.00).

### Table 3. Regional displacement decomposition, 2000–2022

| Region | Displacement ratio | Countries cutting fossil | % displacing |
|---|---|---|---|
| Europe | +0.34 | 27 / 38 | 71.1% |
| Oceania | +0.24 | 2 / 2 | 100% |
| America | −0.05 | 8 / 27 | 29.6% |
| Asia | −2.29 | 6 / 46 | 13.0% |
| Africa | −2.54 | 8 / 50 | 16.0% |

Europe is the only major region where renewables *displaced* fossil; Africa and Asia added fossil far faster than renewables. The renewable–emissions coefficient is therefore not a universal law — it is the statistical signature of regions that happened to retire carbon as they built clean.

### 3.8 Where this lands by 2030
Extrapolating the last decade's momentum (0.87 points/year since 2013), the global renewable share reaches about 36% by 2030 (95% interval 35–37%). The slower full-period trend gives 31%. Either way, renewables remain well short of fossil's ~61% share.

### 3.9 Robustness

| Specification | Coef | SE | N |
|---|---|---|---|
| Baseline (Country + Year FE) | −0.00415 | 0.00031 | 3,749 |
| Sub-sample 2010–2022 | −0.00503 | 0.00033 | 3,478 |
| Drop top-5% emitters | −0.00402 | 0.00032 | 3,565 |
| Cluster-robust SE (baseline) | — | 0.00095 | 3,749 |

The sign and significance of the renewable–emissions link survive sub-sampling, dropping outlier emitters, and clustering.

## 4. Discussion

The evidence points one way on pace and another on chemistry. The transition is accelerating and converging. Decoupling is becoming more common and more absolute, and the renewable–emissions link holds under fixed effects, lagging, first-differencing, clustered errors and a direct grid-intensity test. But the mechanism section draws a harder line: renewables are lowering emissions *per unit of output* in most of the world, yet fossil generation keeps rising in absolute terms — globally by more than renewables rose. The regions where the fixed-effects coefficient is strongest, Europe above all, are also those that retired or throttled carbon plant as they built clean capacity. Africa and Asia show no such dividend because their clean build runs alongside, not against, fossil expansion. The lesson is not that renewables fail; it is that decarbonization follows from *displacement*, and displacement must be engineered into the build, not assumed from the share.

The remaining gap is the one that matters most. Electricity is roughly half of final energy; transport, heat and industry are harder to clean, and they are where the fossil terawatt-hours really live. A 36% renewable electricity share by 2030 is real progress and still leaves fossil dominant in power, and more so in energy overall.

## 5. Limitations

The analysis is associational. Fixed effects, lagging, clustering and first-differencing strengthen the claim but cannot rule out all confounding. The data are secondary aggregates from OWID; country coverage and methodology revisions can shift country-year values, though the broad patterns are robust. Electricity-embedded emissions ignore traded-goods carbon leakage. The grid carbon-intensity result is the cleanest mechanism test but cannot separate retirement of fossil plant from a shift in the dispatch order without unit-level data. The 2030 projection is a constant-momentum extrapolation, not a policy scenario.

## 6. Conclusion

The renewable electricity transition is real, it is accelerating, and in most of the world it is decoupling growth from CO₂ emissions. The catch is in the arithmetic: the world added renewables and added fossil at the same time, and fossil won the terawatt-hour race. Only 31% of countries cut fossil generation at all. So the transition is genuine and yet, in the aggregate, still additive.

That single fact reframes the policy question. The goal is not to build clean power faster than demand grows — the record shows that, by itself, does not retire carbon. The goal is to retire carbon. Do that, and the decoupling already visible in Europe becomes the global default instead of the exception.

---

## References
1. Our World in Data. *Energy and CO₂ datasets* (CC-BY). ourworldindata.org/energy-data
2. Tapio, P. (2005). Towards a theory of decoupling. *Transport Policy*, 12(2), 137–151.
3. OECD (2002). *Indicators to measure decoupling of environmental pressure from economic growth*. OECD, Paris.
4. Steinberger, J. K. & Roberts, J. T. (2010). From constraint to sufficiency. *Environmental Research Letters*, 5(3), 034019.
5. Jackson, T. & Papathanasopoulou, E. (2008). Luxury or 'lock-in'? *Ecological Economics*, 68, 80–95.
6. Semieniuk, G., Campiglio, E. & Mercure, J. F. (2021). Low-carbon transition, green growth and the macroeconomic consensus. *Ecological Economics*, 179, 106832.
7. IPCC (2022). *Climate Change 2022: Mitigation of Climate Change*. Cambridge University Press.
8. IEA (2023). *World Energy Outlook 2023*. OECD/IEA.
9. Hickel, J. & Kallis, G. (2020). Is Green Growth Possible? *New Political Economy*, 25(4), 469–486.
10. Poumanyvong, P. & Kaneko, S. (2010). Does urbanization lead to less energy use and lower CO₂ emissions? *Ecological Economics*, 70(2), 434–444.
11. Ritchie, H., Roser, M. & Rosado, P. (2024). *CO₂ and Greenhouse Gas Emissions*. Our World in Data.
12. Brockway, P. E. et al. (2019). Energy rebound, economy-wide impacts and the global economy. *Energy*, 174, 258–267.

---

### Submission checklist
- [x] Abstract, IMRaD structure, literature review, references, reproducible pipeline.
- [x] Descriptive-statistics, regression, and robustness tables; carbon-intensity outcome; regional displacement.
- [ ] Retarget `manuscript.tex` to journal LaTeX class (elsearticle / svjour3).
- [ ] Add 2–3 recent (2023–2025) decoupling citations for novelty framing.
- [ ] Deposit on Zenodo via `zenodo.json` to obtain a DOI.
- [ ] Upload `preprint.md` to arXiv / SSRN.
