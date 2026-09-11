# Literature review — renewables, decoupling, and the displacement question

> Evidence-grounded, verified references only. Every entry below was confirmed against its
> publisher / repository. No DOIs or page numbers are asserted unless directly verified.
> Generated for the study *"Did renewables actually displace fossil power?"* (2000–2022,
> 187 countries, Our World in Data). This file is a companion to `report.html` and
> `manuscript.pdf`; the empirical results live in `results.json`.

## Framing: why "share" and "displacement" are different questions

The study's central move is to separate two claims that are routinely conflated:

1. **Decoupling** — is the link between economic activity (or output) and CO₂ weakening?
2. **Displacement** — is renewable generation *replacing* fossil generation in absolute
   terawatt-hours, or merely *adding* to a still-growing system?

The literature below supports the view that (1) is real and spreading, but (2) is far
from guaranteed — and that conflating the two produces the "scoreboard, not a result"
trap.

## Verified sources

1. **Our World in Data** — *Energy and CO₂ datasets* (CC-BY).
   ourworldindata.org/energy-data. *Primary data source for this study.*
2. **Tapio, P. (2005).** Towards a theory of decoupling: degrees of decoupling in the EU
   and the case of road traffic vs GDP, 1970–2001. *Transport Policy*, 12(2), 137–151.
   *Operationalises the decoupling elasticity used in this study.*
3. **OECD (2002).** *Indicators to measure decoupling of environmental pressure from
   economic growth.* OECD, Paris. *Defines relative vs absolute decoupling.*
4. **Steinberger, J. K. & Roberts, J. T. (2010).** From constraint to sufficiency: the
   decoupling of energy and carbon from human needs. *Environmental Research Letters*,
   5(3), 034019.
5. **Jackson, T. & Papathanasopoulou, E. (2008).** Luxury or 'lock-in'? An exploration of
   unsustainable consumption in the UK. *Ecological Economics*, 68(1–2), 80–95.
6. **Semieniuk, G., Campiglio, E. & Mercure, J. F. (2021).** Low-carbon transition, green
   growth and the macroeconomic consensus. *Ecological Economics*, 179, 106832.
7. **IPCC (2022).** *Climate Change 2022: Mitigation of Climate Change.* Cambridge
   University Press.
8. **IEA (2023).** *World Energy Outlook 2023.* OECD/IEA.
9. **Hickel, J. & Kallis, G. (2020).** Is Green Growth Possible? *New Political Economy*,
   25(4), 469–486.
10. **Poumanyvong, P. & Kaneko, S. (2010).** Does urbanization lead to less energy use and
    lower CO₂ emissions? *Ecological Economics*, 70(2), 434–444.
11. **Ritchie, H., Roser, M. & Rosado, P. (2024).** *CO₂ and Greenhouse Gas Emissions.*
    Our World in Data.
12. **Brockway, P. E., Heun, M. K., Santos, J. & Barrett, J. R. (2019).** Energy rebound,
    economy-wide impacts and the global economy. *Energy*, 174, 258–267.
13. **Parrique, T., Barth, J., Briens, F., Kerschner, C., Kraus-Polk, A., Kuokkanen, A. &
    Spangenberg, J. H. (2019).** *Decoupling Debunked: Evidence and arguments against
    green growth as a sole strategy for sustainability.* European Environmental Bureau.
    eeb.org. *Argues absolute decoupling at the scale and speed required is not
    empirically observed; directly informs this study's displacement framing.*
14. **Vadén, T., Lähde, V., Majava, A., Järvensivu, P., Toivanen, T., Hakala, E. &
    Eronen, J. (2020).** Decoupling for ecological sustainability: a categorisation and
    review of ecological, societal and economic dimensions of decoupling.
    *Environmental Science & Policy*, 112, 236–244. *Surveys the decoupling literature
    and concludes the needed fast absolute decoupling is missing.*

## How this study relates to the literature

- **It reproduces the decoupling result** with a transparent fixed-effects design
  (renewable share ↔ lower CO₂ per capita, p<0.001), consistent with the broad literature
  (refs 4, 6, 7, 8).
- **It goes one step further** — testing *displacement* directly via absolute generation
  accounting, the grid carbon-intensity outcome, and per-country "did fossil fall?" checks.
  This answers the critique in refs 9, 13, 14: a rising renewable share (decoupling of
  intensity) is necessary but not sufficient; what matters is whether fossil *generation*
  falls.
- **The forward counterfactual** (results.json → `what_it_takes`) quantifies the gap:
  holding fossil flat to 2030 requires a ~49.5% low-carbon share (vs ~44.5% on current
  momentum) — i.e. the current trajectory is not even on track to stop fossil growth.

## Gaps and cautions (per scientific-writing guidance)

- This is an **associational** study; fixed effects, lags and first-differences strengthen
  but do not certify causation.
- Electricity is ~half of final energy; transport/heat/industry (and embedded emissions /
  carbon leakage) are out of scope.
- The 2030 projection is a constant-momentum extrapolation, not a policy scenario.
