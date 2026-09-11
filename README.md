# Did renewables actually displace fossil power?

A reproducible, cross-country analysis of whether a **rising renewable-electricity share
actually displaced fossil generation** — or merely *added* to a still-growing system.

**Headline finding:** Decoupling of *carbon intensity* is real and statistically robust,
but *absolute* fossil generation rose in roughly 70% of 187 countries (2000–2022). The
world built clean power **and** more dirty power at the same time. Holding fossil flat to
2030 requires a ~49.5% low-carbon share — current momentum only reaches ~44.5%.

> Full results: `report.html` · Academic PDF: `manuscript.pdf` · Interactive explorer:
> `dashboard.html` · Plain-language reads: `post_zh.md` (中文) / `post_en.md`.

## Reproduce

```bash
pip install pandas numpy statsmodels scipy   # + weasyprint/pandoc for manuscript.pdf
python src/fetch_data.py                     # downloads OWID energy + CO2 CSVs to data/
python src/analysis.py                       # computes results.json + 14 figures
python src/build_report.py                   # -> report.html
python src/build_manuscript.py               # -> manuscript.pdf
python src/build_dashboard.py                # -> dashboard.html (interactive)
python src/build_landing.py                  # -> index.html
python src/verify_consistency.py             # 39 checks: numbers <-> pages
```

All numbers in the pages come from `results.json` (produced by `src/analysis.py`), which is
itself computed from raw OWID data. Every claim is traceable via `sources/manifest.json`.

## Data

- Electricity & CO₂ datasets: **Our World in Data** (CC-BY-4.0) — `ourworldindata.org/energy-data`.
- Scope: 187 countries, 2000–2022, electricity only (~half of final energy).

## Make it citable (before you publish)

1. Replace the placeholders in `src/build_landing.py` / `src/build_report.py`:
   - `your-github-username` and `renewables-vs-fossil` (the GitHub repo URL),
   - `"Your Name"` (author) and the ORCID in `CITATION.cff` / `.zenodo.json`.
2. Archive a version on **Zenodo** (or Figshare) and paste the real DOI into
   `CITATION.cff` (`identifiers.doi`) and `.zenodo.json`. GitHub + Zenodo integration
   mints a DOI automatically on each release tag.
3. License is **CC-BY-4.0** (see `LICENSE`); data © Our World in Data (CC-BY-4.0).

## Project layout

```
src/            analysis + all page builders
data/           raw OWID CSVs (reproducible via fetch_data.py)
results.json    single source of truth for every number
figures/        14 publication-quality PNGs (DPI 300)
sources/        LITERATURE.md + manifest.json (evidence traceability)
*.html/*.pdf    published outputs
CITATION.cff    make-it-citable metadata (GitHub renders this)
.zenodo.json    DOI deposit metadata
```

## License

CC-BY-4.0 — see `LICENSE`. Attribution: this analysis builds on Our World in Data
(CC-BY-4.0).
