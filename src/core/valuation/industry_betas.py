"""Industry-level beta data for Latam markets.

Why this exists separately from `damodaran.py`:
    Damodaran publishes global industry betas. The right beta for a Latam
    PYME is NOT the global industry beta — it should be weighted toward
    the local equity index composition (COLCAP, Merval, S&P/CLX, etc.)

This module:
1. Bundles the global Damodaran industry betas (Jan 2026 update)
2. Provides a default-weighted beta for each major Latam index
   (computed from the index composition — see `index_composition.json`)
3. Lets the user select beta by industry OR by index.

Selection precedence (highest authority first):
    1. User-provided explicit beta_unlevered (manual override)
    2. Industry beta from Damodaran, scaled by local index weight
    3. Damodaran global industry beta (fallback)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class IndustryBeta:
    """Beta data for one industry (Damodaran)."""

    industry: str
    n_firms: int
    beta_levered: float
    debt_to_equity: float
    effective_tax_rate: float
    unlevered_beta: float  # the number most use
    unlevered_beta_cash_adj: float  # unlevered beta corrected for cash


@dataclass(frozen=True)
class IndexComposition:
    """An equity index's sector composition."""

    country_code: str  # "CO", "AR", etc.
    index_name: str  # "COLCAP", "Merval", etc.
    as_of: str  # ISO date
    sectors: dict[str, float]  # industry -> weight (must sum to 1.0)
    weighted_beta_unlevered: float  # computed: sum(weight * beta)


# ------------------------------------------------------------
# Damodaran global industry betas (Jan 2026, from betaGlobal.xls).
# Subset focused on PYME-relevant sectors.
# ------------------------------------------------------------
INDUSTRY_BETAS: dict[str, IndustryBeta] = {
    "Advertising": IndustryBeta("Advertising", 419, 1.273, 0.406, 0.135, 0.977, 1.086),
    "Aerospace/Defense": IndustryBeta("Aerospace/Defense", 319, 1.231, 0.130, 0.109, 1.122, 1.167),
    "Air Transport": IndustryBeta("Air Transport", 150, 0.991, 0.789, 0.146, 0.624, 0.684),
    "Apparel": IndustryBeta("Apparel", 1207, 0.762, 0.187, 0.152, 0.669, 0.705),
    "Auto & Truck": IndustryBeta("Auto & Truck", 165, 1.406, 0.478, 0.116, 1.036, 1.145),
    "Bank (Money Center)": IndustryBeta("Bank (Money Center)", 604, 0.697, 2.117, 0.216, 0.270, 0.363),
    "Banks (Regional)": IndustryBeta("Banks (Regional)", 825, 0.513, 2.023, 0.184, 0.205, 0.300),
    "Beverage (Alcoholic)": IndustryBeta("Beverage (Alcoholic)", 217, 0.793, 0.203, 0.176, 0.688, 0.725),
    "Beverage (Soft)": IndustryBeta("Beverage (Soft)", 94, 0.593, 0.187, 0.133, 0.520, 0.542),
    "Broadcasting": IndustryBeta("Broadcasting", 127, 0.832, 0.568, 0.152, 0.585, 0.656),
    "Brokerage & Investment Banking": IndustryBeta("Brokerage & Investment Banking", 623, 0.985, 1.791, 0.154, 0.421, 0.490),
    "Building Materials": IndustryBeta("Building Materials", 469, 1.005, 0.228, 0.167, 0.859, 0.903),
    "Business & Consumer Services": IndustryBeta("Business & Consumer Services", 994, 0.992, 0.206, 0.158, 0.860, 0.908),
    "Cable TV": IndustryBeta("Cable TV", 42, 1.097, 1.242, 0.100, 0.569, 0.591),
    "Chemical (Basic)": IndustryBeta("Chemical (Basic)", 909, 1.256, 0.505, 0.147, 0.912, 1.002),
    "Chemical (Specialty)": IndustryBeta("Chemical (Specialty)", 952, 1.154, 0.235, 0.157, 0.981, 1.043),
    "Coal & Related Energy": IndustryBeta("Coal & Related Energy", 212, 1.143, 0.199, 0.107, 0.995, 1.133),
    "Computer Services": IndustryBeta("Computer Services", 1225, 1.117, 0.150, 0.166, 1.004, 1.072),
    "Computers/Peripherals": IndustryBeta("Computers/Peripherals", 343, 1.486, 0.062, 0.129, 1.420, 1.453),
    "Construction Supplies": IndustryBeta("Construction Supplies", 804, 1.034, 0.303, 0.167, 0.844, 0.910),
    "Drugs (Biotechnology)": IndustryBeta("Drugs (Biotechnology)", 1193, 1.231, 0.123, 0.021, 1.127, 1.165),
    "Drugs (Pharmaceutical)": IndustryBeta("Drugs (Pharmaceutical)", 1260, 1.063, 0.149, 0.104, 0.956, 0.989),
    "Education": IndustryBeta("Education", 281, 0.812, 0.286, 0.145, 0.669, 0.745),
    "Engineering/Construction": IndustryBeta("Engineering/Construction", 1390, 1.001, 0.766, 0.177, 0.637, 0.760),
    "Environmental & Waste Services": IndustryBeta("Environmental & Waste Services", 397, 1.102, 0.357, 0.128, 0.870, 0.908),
    "Food Processing": IndustryBeta("Food Processing", 1450, 0.674, 0.371, 0.164, 0.528, 0.561),
    "Food Wholesalers": IndustryBeta("Food Wholesalers", 183, 0.685, 0.582, 0.174, 0.477, 0.498),
    "Healthcare Products": IndustryBeta("Healthcare Products", 842, 1.182, 0.139, 0.085, 1.071, 1.118),
    "Healthcare Support Services": IndustryBeta("Healthcare Support Services", 478, 0.917, 0.381, 0.146, 0.714, 0.779),
    "Homebuilding": IndustryBeta("Homebuilding", 160, 0.960, 0.399, 0.197, 0.740, 0.822),
    "Hospitals/Healthcare Facilities": IndustryBeta("Hospitals/Healthcare Facilities", 249, 0.760, 0.466, 0.185, 0.564, 0.583),
    "Information Services": IndustryBeta("Information Services", 86, 1.024, 0.320, 0.198, 0.826, 0.873),
    "Machinery": IndustryBeta("Machinery", 1553, 1.369, 0.136, 0.160, 1.244, 1.330),
    "Oil/Gas (Integrated)": IndustryBeta("Oil/Gas (Integrated)", 124, 0.893, 0.275, 0.190, 0.764, 0.825),
    "Oil/Gas (Production and Exploration)": IndustryBeta("Oil/Gas (Production and Exploration)", 547, 1.190, 0.342, 0.116, 0.967, 1.115),
    "Oilfield Svcs/Equip.": IndustryBeta("Oilfield Svcs/Equip.", 165, 1.422, 0.246, 0.139, 1.214, 1.327),
    "Office Equipment & Services": IndustryBeta("Office Equipment & Services", 139, 0.759, 0.286, 0.162, 0.625, 0.711),
    "Real Estate (Development)": IndustryBeta("Real Estate (Development)", 285, 0.974, 0.913, 0.114, 0.535, 0.622),
    "Real Estate (Operations & Services)": IndustryBeta("Real Estate (Operations & Services)", 752, 0.782, 0.825, 0.143, 0.484, 0.515),
    "Restaurant/Dining": IndustryBeta("Restaurant/Dining", 410, 0.755, 0.260, 0.152, 0.632, 0.661),
    "Retail (Automotive)": IndustryBeta("Retail (Automotive)", 212, 0.835, 0.527, 0.169, 0.599, 0.629),
    "Retail (Building Supply)": IndustryBeta("Retail (Building Supply)", 121, 0.945, 0.260, 0.184, 0.792, 0.806),
    "Retail (Distributors)": IndustryBeta("Retail (Distributors)", 1079, 0.814, 0.483, 0.175, 0.598, 0.642),
    "Retail (General)": IndustryBeta("Retail (General)", 252, 0.983, 0.130, 0.177, 0.895, 0.937),
    "Retail (Grocery and Food)": IndustryBeta("Retail (Grocery and Food)", 215, 0.874, 0.460, 0.208, 0.650, 0.679),
    "Retail (Online)": IndustryBeta("Retail (Online)", 87, 1.354, 0.069, 0.140, 1.281, 1.314),
    "Retail (REITs)": IndustryBeta("Retail (REITs)", 113, 0.608, 0.711, 0.068, 0.397, 0.408),
    "Retail (Special Lines)": IndustryBeta("Retail (Special Lines)", 649, 0.960, 0.184, 0.169, 0.845, 0.879),
    "Shipbuilding & Marine": IndustryBeta("Shipbuilding & Marine", 359, 0.874, 0.417, 0.151, 0.667, 0.789),
    "Software (Entertainment)": IndustryBeta("Software (Entertainment)", 298, 1.246, 0.031, 0.109, 1.218, 1.236),
    "Software (Internet)": IndustryBeta("Software (Internet)", 150, 1.392, 0.100, 0.113, 1.295, 1.336),
    "Software (System & Application)": IndustryBeta("Software (System & Application)", 1532, 1.354, 0.058, 0.090, 1.297, 1.331),
    "Steel": IndustryBeta("Steel", 312, 1.341, 0.345, 0.142, 1.079, 1.169),
    "Telecom. Equipment": IndustryBeta("Telecom. Equipment", 580, 1.182, 0.196, 0.108, 1.041, 1.090),
    "Telecom. Services": IndustryBeta("Telecom. Services", 283, 0.729, 0.732, 0.154, 0.471, 0.520),
    "Transportation": IndustryBeta("Transportation", 451, 0.964, 0.535, 0.176, 0.689, 0.747),
    "Transportation (Railroads)": IndustryBeta("Transportation (Railroads)", 54, 0.720, 0.474, 0.242, 0.532, 0.554),
    "Trucking": IndustryBeta("Trucking", 130, 0.850, 0.399, 0.200, 0.655, 0.678),
    "Utility (General)": IndustryBeta("Utility (General)", 270, 0.518, 0.875, 0.155, 0.302, 0.339),
    "Utility (Water)": IndustryBeta("Utility (Water)", 39, 0.580, 0.652, 0.196, 0.388, 0.432),
}


def beta_for_industry(industry: str) -> IndustryBeta:
    if industry not in INDUSTRY_BETAS:
        raise ValueError(
            f"Unknown industry: {industry!r}. "
            f"Available: {sorted(INDUSTRY_BETAS.keys())}"
        )
    return INDUSTRY_BETAS[industry]


def beta_for_index_country(country_code: str) -> float:
    """Return the unlevered beta implied by a country's main equity index composition.

    Reads from `data/index_composition.json`. If the country isn't there,
    raises FileNotFoundError with a helpful message.

    Sectors present in the composition file but missing from Damodaran's
    INDUSTRY_BETAS dict are reported via stderr (so users know they need
    to map them) and skipped from the weighted average. The returned beta
    is therefore the best estimate given available data, not a fixed answer.
    """
    import sys
    path = Path(__file__).resolve().parents[3] / "data" / "index_composition.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Index composition file not found at {path}. "
            f"See docs/methodology.md#equity-index-composition for the expected format."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if country_code not in payload:
        raise ValueError(
            f"No index composition for country {country_code!r}. "
            f"Available: {list(payload.keys())}"
        )
    comp = payload[country_code]
    sectors: dict[str, float] = comp["sectors"]
    beta_weighted = 0.0
    total_weight = 0.0
    missing_sectors = []
    for industry, weight in sectors.items():
        if industry not in INDUSTRY_BETAS:
            missing_sectors.append((industry, weight))
            continue
        beta_weighted += weight * INDUSTRY_BETAS[industry].unlevered_beta
        total_weight += weight

    if missing_sectors:
        print(
            f"[WARN] {country_code}: {len(missing_sectors)} sector(s) not in INDUSTRY_BETAS — "
            f"weighted beta uses {total_weight*100:.1f}% of total weight:",
            file=sys.stderr,
        )
        for s, w in missing_sectors:
            print(f"  - {s} ({w*100:.1f}%)", file=sys.stderr)

    if total_weight < 0.99:
        print(
            f"[WARN] {country_code}: only {total_weight*100:.1f}% of index weight mapped to "
            f"known Damodaran industries. Beta is incomplete.",
            file=sys.stderr,
        )

    return beta_weighted


def list_industries() -> list[str]:
    """Return all available industry names (alphabetical)."""
    return sorted(INDUSTRY_BETAS.keys())
