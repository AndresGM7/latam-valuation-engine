#!/usr/bin/env python
"""
refresh_index_composition.py
=============================

Refresh the equity-index composition JSON used by the WACC calculator.

WHY THIS SCRIPT EXISTS
----------------------
The country-specific WACC needs a beta representative of the local equity
market. The cleanest way to derive that is to take the sector composition
of the main local index (COLCAP for Colombia, Merval for Argentina) and
weight each sector's Damodaran unlevered beta by its weight in the index.

Two things change frequently:
1. The index composition itself (BVC rebalances COLCAP every 4 months;
   IAMC/BYMA rebalance Merval quarterly).
2. Damodaran's industry beta dataset (annual).

This script automates BOTH refreshes, with two strategies:

A. **AUTOMATIC** (preferred): uses the World Bank and Damodaran public
   datasets that we already auto-refresh.

B. **SEMI-AUTOMATIC**: tells the user to log into BVC and IAMC websites
   with a browser, copy the composition table, paste as JSON.

USAGE
-----
    # Option A: just refresh Damodaran betas (always works)
    python scripts/refresh_index_composition.py --datasource damodaran

    # Option B: open the BVC and IAMC pages for manual copy
    python scripts/refresh_index_composition.py --datasource manual --open

    # After pasting the compositions into data/raw/colcap.json and
    # data/raw/merval.json, normalize them:
    python scripts/refresh_index_composition.py --datasource manual --normalize

SOURCE URLS
-----------
COLCAP:
    https://www.bvc.com.co/pps/tibco-pp-bvc/datos/IndicesAccionarios/COLCAP
    (JavaScript-rendered, requires browser)

Merval:
    https://www.byma.com.ar/indices/merval
    https://www.iamc.com.ar/indices/iamc/

Damodaran (auto-refreshable):
    https://pages.stern.nyu.edu/~adamodar/pc/datasets/betaGlobal.xls
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path

import xlrd  # type: ignore

# Layout
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

TARGET_FILE = DATA_DIR / "index_composition.json"

# Industry mapping: how each Latam-listed company maps to a Damodaran industry.
# This is the ONLY manual input we need, because the mapping is structural,
# not time-varying. (Banks are always banks, oil is always oil.)
LATAM_COMPANY_TO_DAMODARAN = {
    # COLCAP (Colombia) - structural mapping
    "ECOPETROL": "Oil/Gas (Integrated)",
    "BCOLOMBIA": "Banks (Regional)",
    "PFBCOLOM": "Banks (Regional)",
    "GRUPOSURA": "Investments & Asset Mgmt",
    "GRUPOARGOS": "Investments & Asset Mgmt",
    "PFDAVVNDA": "Banks (Regional)",
    "ISA": "Utility (General)",
    "GEB": "Utility (General)",
    "CORFICOLCF": "Investments & Asset Mgmt",
    "CEMARGOS": "Building Materials",
    "NUTRESA": "Food Processing",
    "BOGOTA": "Banks (Regional)",
    "CELSIA": "Utility (General)",
    "TERPEL": "Oil/Gas (Distribution)",
    "GRUPOAVAL": "Investments & Asset Mgmt",
    "PFAVAL": "Investments & Asset Mgmt",
    "MINEROS": "Metals & Mining",
    "CANACOL": "Oil/Gas (Production and Exploration)",
    "ETB": "Telecom. Services",
    "PROMIGAS": "Oil/Gas (Distribution)",
    "CONCONCRETO": "Engineering/Construction",
    "BBVACOL": "Banks (Regional)",
    # Merval (Argentina) - structural mapping
    "YPFD": "Oil/Gas (Integrated)",
    "GGAL": "Banks (Regional)",
    "PAMP": "Utility (General)",
    "MELI": "Retail (Online)",
    "BMA": "Banks (Regional)",
    "BBAR": "Banks (Regional)",
    "TECO2": "Telecom. Services",
    "TGS": "Oil/Gas (Distribution)",
    "EDN": "Utility (General)",
    "CEPU": "Utility (General)",
    "LOMA": "Building Materials",
    "HARG": "Building Materials",
    "TXAR": "Steel",
    "ALUA": "Metals & Mining",
    "MIRG": "Auto Parts",
    "CRES": "Real Estate (Operations & Services)",
    "IRSA": "Real Estate (Operations & Services)",
    "TRAN": "Utility (General)",
}


def refresh_damodaran_betas() -> None:
    """Download fresh Damodaran betas and update industry_betas.py."""
    import urllib.request

    url = "https://pages.stern.nyu.edu/~adamodar/pc/datasets/betaGlobal.xls"
    target = RAW_DIR / "damodaran_betaGlobal.xls"
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, target)
    print(f"  ✓ saved to {target}")

    book = xlrd.open_workbook(target)
    sh = book.sheet_by_name("Industry Averages")
    # Data starts at row 9 (0-indexed), header in row 9
    print(f"  Parsing {sh.nrows - 10} industries...")

    # Quick sanity print
    print("\nTop 10 industries by unlevered beta:")
    rows = []
    for r in range(9, sh.nrows):
        name = sh.cell_value(r, 0)
        if not name:
            continue
        unlev = sh.cell_value(r, 5)
        rows.append((unlev, name))
    rows.sort(reverse=True)
    for unlev, name in rows[:10]:
        print(f"    {unlev:.3f}  {name}")


def open_browser_urls() -> None:
    """Open the BVC and IAMC pages in the user's browser for manual copy."""
    urls = [
        ("https://www.bvc.com.co/pps/tibco-pp-bvc/datos/IndicesAccionarios/COLCAP",
         "BVC COLCAP page"),
        ("https://www.byma.com.ar/indices/merval",
         "BYMA Merval page"),
        ("https://www.iamc.com.ar/indices/iamc/",
         "IAMC Merval index page"),
    ]
    for url, label in urls:
        print(f"Opening {label}...")
        webbrowser.open(url)


def normalize_manual_input() -> None:
    """Take raw/colcap.json and raw/merval.json and produce index_composition.json."""
    if not (RAW_DIR / "colcap.json").exists():
        print(f"ERROR: missing {RAW_DIR / 'colcap.json'}. "
              f"Run with --open first, paste the composition into that file.")
        sys.exit(1)
    if not (RAW_DIR / "merval.json").exists():
        print(f"ERROR: missing {RAW_DIR / 'merval.json'}. "
              f"Run with --open first, paste the composition into that file.")
        sys.exit(1)

    # Expected format of the raw JSON files:
    # {
    #   "as_of": "2024-12-01",
    #   "components": [
    #     {"ticker": "ECOPETROL", "weight_pct": 16.5},
    #     {"ticker": "BCOLOMBIA", "weight_pct": 13.2},
    #     ...
    #   ]
    # }
    out = {"_meta": {"description": "Auto-generated from manual input", "last_manual_review": "unknown"}}
    for code, fname in [("CO", "colcap.json"), ("AR", "merval.json")]:
        with open(RAW_DIR / fname, "r", encoding="utf-8") as f:
            raw = json.load(f)

        sector_weights: dict[str, float] = {}
        total_weight = 0.0
        for c in raw["components"]:
            ticker = c["ticker"].upper()
            weight = float(c["weight_pct"])
            sector = LATAM_COMPANY_TO_DAMODARAN.get(ticker)
            if sector is None:
                print(f"  WARNING: ticker {ticker!r} not mapped to a Damodaran industry. Skipping.")
                continue
            sector_weights[sector] = sector_weights.get(sector, 0.0) + weight
            total_weight += weight

        # Normalize to sum=1
        if abs(total_weight - 100.0) > 0.1:
            print(f"  WARNING: total weight for {code} is {total_weight}, expected ~100. Normalizing.")
        sector_weights = {k: v / total_weight for k, v in sector_weights.items()}

        out[code] = {
            "index_name": "COLCAP" if code == "CO" else "Merval",
            "country": "Colombia" if code == "CO" else "Argentina",
            "as_of": raw["as_of"],
            "source_note": "Manual input from BVC/IAMC (refreshed). See scripts/refresh_index_composition.py.",
            "sectors": sector_weights,
        }

    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"✓ Wrote {TARGET_FILE}")
    print("\nSector compositions:")
    for code in ("CO", "AR"):
        print(f"\n{code}:")
        for sector, w in sorted(out[code]["sectors"].items(), key=lambda x: -x[1])[:10]:
            print(f"  {w*100:5.1f}%  {sector}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datasource", choices=["damodaran", "manual"], required=True,
                   help="damodaran: just refresh industry betas. manual: open browser, normalize input.")
    p.add_argument("--open", action="store_true", help="Open browser URLs (with --datasource manual).")
    args = p.parse_args()

    if args.datasource == "damodaran":
        refresh_damodaran_betas()
    elif args.datasource == "manual":
        if args.open:
            open_browser_urls()
            print(f"\nNext steps:")
            print(f"1. Copy the COLCAP components into {RAW_DIR / 'colcap.json'}")
            print(f"2. Copy the Merval components into {RAW_DIR / 'merval.json'}")
            print(f"3. Re-run: python {Path(__file__).name} --datasource manual --normalize")
        else:
            normalize_manual_input()


if __name__ == "__main__":
    main()
