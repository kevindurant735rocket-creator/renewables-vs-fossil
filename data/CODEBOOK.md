# Data Codebook & Provenance

This project is fully reproducible. Run `python src/fetch_data.py` to download the
two raw inputs, then `python src/analysis.py` to regenerate every number and figure.

## Sources

| File | Provider | License | Raw URL |
|---|---|---|---|
| `owid-energy-data.csv` | Our World in Data — *Energy* | CC-BY | `https://github.com/owid/energy-data/raw/master/owid-energy-data.csv` |
| `owid-co2-data.csv` | Our World in Data — *CO₂* | CC-BY | `https://github.com/owid/co2-data/raw/master/owid-co2-data.csv` |

## Sample construction (`analysis.py`)

1. Keep rows with a non-missing `iso_code` that does **not** start with `OWID` (drops aggregates such as "World", "Europe", "High-income countries").
2. Restrict to `year >= 2000` (study window 2000–2022).
3. Inner-join the energy and CO₂ tables on `(iso_code, year)`.
4. Require non-missing: `renewables_share_elec`, `fossil_share_elec`, `low_carbon_share_elec`, `co2`, `gdp`, `population`, `electricity_generation`, `carbon_intensity_elec`.
5. Result: **163 countries, 3,749 country-year observations**.

## Variables used

| Variable | Definition | Notes |
|---|---|---|
| `renewables_share_elec` | Renewables as % of electricity generation | Primary explanatory variable |
| `fossil_share_elec` | Fossil fuels as % of electricity generation | = 100 − `low_carbon_share_elec` |
| `low_carbon_share_elec` | Low-carbon (renewables + nuclear) as % of generation | |
| `co2` | CO₂ emissions (million tonnes) | OWID reports in **million tonnes** — see unit fix below |
| `co2_per_capita` | CO₂ per capita (tonnes) | Recomputed as `co2 × 1e6 / population` |
| `gdp` | GDP (international $, constant) | |
| `gdp_per_capita` | `gdp / population` | |
| `population` | Population (persons) | |
| `electricity_generation` | Total electricity generation (TWh) | Used for absolute displacement accounting |
| `electricity_demand_per_capita` | `electricity_demand / population` | Demand-control variable |
| `carbon_intensity_elec` | CO₂ per kWh of electricity (gCO₂/kWh) | Second outcome (direct displacement test) |
| `region` | OWID geographical region | Used for regional heterogeneity & displacement decomposition |

## Unit fix (important)

OWID stores `co2` in **million tonnes**. The natural per-capita quantity is therefore
`co2 × 1e6 / population` (tonnes per person). An earlier draft divided `co2 / population`
directly, understating per-capita CO₂ by a factor of 1,000,000 and making the descriptive
table show `0.0`. The corrected computation is in `analysis.py`:

```python
df["co2_per_capita"] = df["co2"] * 1e6 / df["population"]
```

All regressions use `ln(co2_per_capita)` and are unaffected by the linear scaling, but the
descriptive-statistics table and the regional means depend on the correct unit.

## Derived quantities

- **β-convergence**: regress each country's annual log growth in `renewables_share_elec` on its 2000 level.
- **σ-convergence**: track the cross-country SD of `renewables_share_elec` over time.
- **Tapio decoupling**: `DI = (%ΔCO₂) / (%ΔGDP)` over 5-year rolling windows; classified into absolute / relative decoupling, coupling, expansive coupling, and recession.
- **Two-way FE**: `ln(CO₂/capita) ~ renewables_share_elec + ln(GDP/capita) + country FE + year FE`.
- **Second outcome**: `ln(grid carbon intensity) ~ renewables_share_elec + ln(GDP/capita) + FE`.
- **Displacement ratio**: `−ΔFossilGen / ΔRenewGen` per country, 2000→2022; positive = renewables displaced fossil.

## Outputs

- `results.json` — every statistic the paper cites (single source of truth).
- `figures/*.png` — 12 publication-quality figures (DPI 300).
- `report.html`, `dashboard.html`, `manuscript.tex`/`manuscript.pdf`, `preprint.md`, `post_zh.md`, `policy_brief.html`.
