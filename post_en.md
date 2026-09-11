# Did renewables actually *displace* fossil power?

> A plain-language explainer · Data: Our World in Data (CC-BY) · 187 countries · 2000–2022

## The one-line answer

Renewables are clearly **lowering carbon emissions per unit of output** — but in most countries they are being *added on top of* a still-growing fossil system, not *replacing* it.

## Three facts that matter

1. **The share rose, but so did the total.** Between 2000 and 2022, renewables went from 18.6% to 31% of global electricity. Over the same period, **fossil generation rose by ~7,861 TWh** — almost as much as the renewable increase (~8,495 TWh). The world built clean power *and* built more dirty power at the same time.

2. **Only ~31% of countries actually cut fossil generation.** The other ~70% burned more. A country's renewable-share gain tells you almost nothing about whether its coal and gas fell (correlation ≈ 0).

3. **Per-capita CO₂ really did fall.** Holding country and year fixed, each +1 percentage-point of renewable share is associated with about **−0.61% lower CO₂ per capita** (p<0.001), strongest in Europe (−0.53%/pp) and the Americas (−0.76%/pp). The "intensity" dividend is real — it just isn't the same as burning less fossil fuel.

## Why this matters

- There are two kinds of **decoupling**: *relative* (emissions rise slower than GDP) and *absolute* (emissions fall outright). A rising renewable share is often a scoreboard for relative decoupling, not a result of absolute decoupling.
- The literature (Parrique et al. 2019; Vadén et al. 2020) has long argued the fast, *absolute* decoupling the climate needs isn't yet observed empirically. This study measures displacement directly, with generation-level accounting, and confirms the gap.

## Where this lands by 2030

At current momentum, fossil generation **keeps rising** — from ~17,693 TWh (2022) to about **19,345 TWh (2030)**.

The more useful question runs the other way: **to keep fossil generation no higher than today, the low-carbon share would have to reach ~49.5% by 2030** — but momentum only delivers ~44.5%, roughly 5 points short of even stopping the growth. Cutting fossil 30% needs ~64.7%.

## Bottom line

This isn't anti-renewables. It's a reminder that the transition must be about **displacement, not addition**. Retiring coal and gas — letting renewables squeeze them out — is the part that hasn't happened yet. Otherwise 2030 arrives with a greener scoreboard and a warmer planet.

## Explore it yourself

- Interactive dashboard (any country): `dashboard.html`
- Full report: `report.html` · Academic PDF: `manuscript.pdf` · Data: `results.json`

*Every number is computed by `src/analysis.py` from raw data and is traceable in `sources/manifest.json`.*
