"""Macroeconomic data loader for Colombia and Argentina.

Sources of truth (manual refresh; update quarterly):
    Colombia:
        - Banrep: https://sucre.banrep.gov.co/
        - DANE: https://www.dane.gov.co/
        - SuperFinanciera: https://www.superfinanciera.gov.co/
    Argentina:
        - BCRA: https://www.bcra.gob.ar/
        - INDEC: https://www.indec.gob.ar/

We DO NOT hit these endpoints in production code yet — that's a v2
feature (data freshness automation). For now, the data lives in
data/macro/{country}.yaml and is loaded by this module.

The thesis for doing it this way:
    "Free API tier" of Latam macro data doesn't exist in a single
    source. We curate from official sources and document provenance
    in the YAML. This is what consulting firms do internally.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Country(str, Enum):
    COLOMBIA = "CO"
    ARGENTINA = "AR"


class MacroSnapshot(BaseModel):
    """A country's macro snapshot at a point in time."""

    country: Country
    as_of: date
    inflation_yoy_pct: float = Field(..., description="IPC YoY headline")
    inflation_expectations_1y_pct: float = Field(..., description="Market expectations, 1Y")
    inflation_expectations_2y_pct: float = Field(..., description="Market expectations, 2Y")
    reference_rate_pct: float = Field(..., description="Central bank policy rate")
    embi_spread_bps: float = Field(..., description="EMBI spread over US Treasury, basis points")
    country_risk_premium_pct: float = Field(0.0, description="Damodaran-style country risk premium")
    equity_risk_premium_pct: float = Field(0.0, description="Damodaran total ERP (mature + CRP)")
    fx_rate_to_usd: float = Field(..., description="Local currency per USD")
    fx_volatility_30d_pct: float = Field(..., description="30-day realized FX volatility")
    unemployment_pct: float = Field(..., description="National unemployment rate")
    gdp_growth_yoy_pct: float = Field(..., description="Real GDP growth, YoY")
    min_wage_local: float = Field(..., description="Monthly minimum wage in local currency")
    tax_rate_corp_pct: float = Field(0.0, description="Effective corporate tax rate")
    debt_to_gdp_pct: float = Field(0.0, description="Public debt to GDP")
    source: str = Field(..., description="Provenance string")


@dataclass
class MacroLoader:
    """Loads macroeconomic snapshots from data/macro/{country}.yaml."""

    data_dir: Path

    def load(self, country: Country) -> MacroSnapshot:
        filename = "colombia.yaml" if country == Country.COLOMBIA else "argentina.yaml"
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Macro data file not found: {path}. "
                f"Create it from data/macro/{filename}.example or run "
                f"`python scripts/update_macro_data.py` to fetch."
            )
        with path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        return MacroSnapshot(**raw)


# Convenience singleton with sensible default path
_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "macro"
_default_loader = MacroLoader(data_dir=_DEFAULT_DATA_DIR)


def load_macro(country: Country) -> MacroSnapshot:
    """Convenience function: load the latest macro snapshot for a country."""
    return _default_loader.load(country)


__all__ = ["Country", "MacroSnapshot", "MacroLoader", "load_macro"]
