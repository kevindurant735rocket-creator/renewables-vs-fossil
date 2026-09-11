"""Fetch the raw Our World in Data (OWID) source files used by analysis.py.

OWID publishes these as CC-BY CSVs on GitHub. Running this script makes the
project reproducible from scratch: after `python src/fetch_data.py` the
`data/` directory holds the exact inputs `analysis.py` expects.

Usage:
    python src/fetch_data.py            # download only if missing
    python src/fetch_data.py --force    # re-download unconditionally
"""
from __future__ import annotations
import argparse
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# OWID energy + CO2 datasets (CC-BY). Raw CSV mirrors on GitHub.
SOURCES = {
    "owid-energy-data.csv": "https://github.com/owid/energy-data/raw/master/owid-energy-data.csv",
    "owid-co2-data.csv": "https://github.com/owid/co2-data/raw/master/owid-co2-data.csv",
}

# Minimal UA so GitHub's raw endpoint is happy behind some proxies.
_HEADERS = {"User-Agent": "Mozilla/5.0 (research-repro; +https://ourworldindata.org)"}


def fetch(name: str, url: str, force: bool) -> None:
    dest = DATA / name
    if dest.exists() and not force:
        print(f"  skip {name} (already present, {dest.stat().st_size/1e6:.1f} MB)")
        return
    print(f"  downloading {name} ...", end=" ", flush=True)
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
    except Exception as exc:  # network/proxy issues
        print(f"FAILED ({exc})")
        print("  -> fetch manually from:")
        print(f"     {url}")
        print(f"     and save to {dest}")
        return
    dest.write_bytes(data)
    print(f"OK ({len(data)/1e6:.1f} MB)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Download OWID raw data for the project.")
    ap.add_argument("--force", action="store_true", help="re-download even if present")
    args = ap.parse_args()
    print(f"Target directory: {DATA}")
    for name, url in SOURCES.items():
        fetch(name, url, args.force)
    print("Done. Now run: python src/analysis.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
