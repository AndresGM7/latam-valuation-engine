"""
Country-specific WACC for Colombia and Argentina.

The thesis:
    Standard WACC = kd*(1-t)*(D/(D+E)) + ke*(E/(D+E))
    Latam-specific WACC = Standard WACC + EMBI spread / country risk premium

Why this matters:
    Big 4 (McKinsey/BCG/PwC) and tier-1 investment banks (Goldman,
    JPMorgan, Morgan Stanley) routinely inflate Latam discount rates
    by 2-8 percentage points to reflect sovereign risk. Most
    off-the-shelf SaaS valuation tools ignore this, so their DCF
    numbers for a Colombian or Argentine SME systematically OVERVALUE
    the business by 30-60%.

If you can show an analyst or investor "their DCF used a US WACC on
a Colombian business" — that's the kind of technical remarkability
that wins consulting roles and SaaS conversions.

References:
    - Damodaran, A. (2024). "Country Risk Premiums and WACC".
    - Banrep. "EMBI Colombia" historical series.
    - INDEC + BCRA. Country risk for Argentina (sovereign spread).
    - J.P. Morgan EMBI Global methodology.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Country(str, Enum):
    COLOMBIA = "CO"
    ARGENTINA = "AR"
    UNITED_STATES = "US"  # baseline; no country risk premium


class WACCInputs(BaseModel):
    """Inputs to compute WACC."""

    country: Country
    risk_free_rate_pct: float = Field(..., ge=0, le=30, description="US 10Y Treasury or local risk-free proxy")
    equity_risk_premium_pct: float = Field(..., ge=0, le=20, description="Damodaran ERP for the country")
    country_risk_premium_pct: float = Field(0.0, ge=0, le=30, description="EMBI spread or sovereign CDS")
    beta_unlevered: float = Field(..., ge=0.1, le=3.0, description="Industry beta from Damodaran")
    debt_to_total_capital_pct: float = Field(..., ge=0, le=100, description="Target D/(D+E)")
    cost_of_debt_pretax_pct: float = Field(..., ge=0, le=50, description="Local currency borrowing rate")
    tax_rate_pct: float = Field(..., ge=0, le=50, description="Effective corporate tax rate")

    @field_validator("risk_free_rate_pct", "equity_risk_premium_pct", "country_risk_premium_pct",
                     "beta_unlevered", "debt_to_total_capital_pct", "cost_of_debt_pretax_pct", "tax_rate_pct")
    @classmethod
    def _finite(cls, v: float) -> float:
        if v != v:  # NaN check
            raise ValueError("NaN not allowed")
        return float(v)


@dataclass
class WACCResult:
    cost_of_equity_pct: float
    cost_of_debt_after_tax_pct: float
    wacc_pct: float
    country_risk_premium_applied_pct: float
    components: dict


def relever_beta(
    beta_unlevered: float,
    debt_to_equity: float,
    tax_rate_pct: float,
) -> float:
    """Re-lever a beta using the Hamada formula.

    beta_levered = beta_unlevered * (1 + (1 - t) * D/E)
    """
    tax_rate = tax_rate_pct / 100.0
    return beta_unlevered * (1.0 + (1.0 - tax_rate) * debt_to_equity)


def compute_wacc(inputs: WACCInputs) -> WACCResult:
    """Compute WACC with country risk premium adjustment.

    Formula:
        ke = rf + beta_levered * ERP + country_risk_premium
        kd_after_tax = kd * (1 - t)
        WACC = ke * (E/V) + kd_after_tax * (D/V)

    Where V = D + E.
    """
    d_over_v = inputs.debt_to_total_capital_pct / 100.0
    e_over_v = 1.0 - d_over_v

    if d_over_v > 0 and e_over_v > 0:
        debt_to_equity = d_over_v / e_over_v
    else:
        debt_to_equity = 0.0

    beta_levered = relever_beta(
        beta_unlevered=inputs.beta_unlevered,
        debt_to_equity=debt_to_equity,
        tax_rate_pct=inputs.tax_rate_pct,
    )

    cost_of_equity = (
        inputs.risk_free_rate_pct
        + beta_levered * inputs.equity_risk_premium_pct
        + inputs.country_risk_premium_pct
    )

    cost_of_debt_after_tax = inputs.cost_of_debt_pretax_pct * (1.0 - inputs.tax_rate_pct / 100.0)

    wacc = cost_of_equity * e_over_v + cost_of_debt_after_tax * d_over_v

    return WACCResult(
        cost_of_equity_pct=cost_of_equity,
        cost_of_debt_after_tax_pct=cost_of_debt_after_tax,
        wacc_pct=wacc,
        country_risk_premium_applied_pct=inputs.country_risk_premium_pct,
        components={
            "rf": inputs.risk_free_rate_pct,
            "beta_levered": beta_levered,
            "erp": inputs.equity_risk_premium_pct,
            "crp": inputs.country_risk_premium_pct,
            "kd_pretax": inputs.cost_of_debt_pretax_pct,
            "kd_after_tax": cost_of_debt_after_tax,
            "D_over_V": d_over_v,
            "E_over_V": e_over_v,
        },
    )


# ------------------------------------------------------------
# Convenience presets calibrated to public data (2024-2026).
# Numbers are intentionally conservative; users can override.
# ------------------------------------------------------------


@dataclass
class CountryDefaults:
    """Default country-level inputs for WACC. Update these as Banrep/SFC publish new data."""

    country: Country
    risk_free_rate_pct: float  # Local 10Y sovereign bond yield (USD-denominated for AR)
    equity_risk_premium_pct: float  # Damodaran-style mature-market premium
    country_risk_premium_pct: float  # Current EMBI / CDS spread
    cost_of_debt_pretax_pct: float  # Avg commercial bank lending rate
    tax_rate_pct: float


# 2026-Q4 calibration. Update from data/macro/ quarterly.
DEFAULTS_2026 = {
    Country.COLOMBIA: CountryDefaults(
        country=Country.COLOMBIA,
        risk_free_rate_pct=4.30,        # US 10Y (Col local bond yield would be higher but US proxy is convention)
        equity_risk_premium_pct=5.50,   # Damodaran Colombia 2024
        country_risk_premium_pct=2.80,  # EMBI Colombia spread over US Treasury
        cost_of_debt_pretax_pct=17.40,  # Tasa Bancos promedio (SFC)
        tax_rate_pct=35.0,              # Tarica nominal Colombia 2024+
    ),
    Country.ARGENTINA: CountryDefaults(
        country=Country.ARGENTINA,
        risk_free_rate_pct=4.30,        # US 10Y proxy
        equity_risk_premium_pct=8.00,   # Damodaran Argentina ERP
        country_risk_premium_pct=8.50,  # Riesgo soberano ARG post-2024 (alto)
        cost_of_debt_pretax_pct=45.00,  # BADLAR + spread, post-devaluacion
        tax_rate_pct=35.0,              # Impuesto a las ganancias
    ),
    Country.UNITED_STATES: CountryDefaults(
        country=Country.UNITED_STATES,
        risk_free_rate_pct=4.30,
        equity_risk_premium_pct=5.50,
        country_risk_premium_pct=0.0,
        cost_of_debt_pretax_pct=6.50,
        tax_rate_pct=21.0,
    ),
}


def wacc_from_defaults(
    country: Country,
    beta_unlevered: float = 1.0,
    debt_to_total_capital_pct: float = 30.0,
) -> WACCResult:
    """Compute WACC using calibrated defaults + user-provided beta and capital structure.

    This is the convenience function most API calls will use.
    """
    defaults = DEFAULTS_2026[country]
    inputs = WACCInputs(
        country=country,
        risk_free_rate_pct=defaults.risk_free_rate_pct,
        equity_risk_premium_pct=defaults.equity_risk_premium_pct,
        country_risk_premium_pct=defaults.country_risk_premium_pct,
        beta_unlevered=beta_unlevered,
        debt_to_total_capital_pct=debt_to_total_capital_pct,
        cost_of_debt_pretax_pct=defaults.cost_of_debt_pretax_pct,
        tax_rate_pct=defaults.tax_rate_pct,
    )
    return compute_wacc(inputs)


__all__ = [
    "Country",
    "WACCInputs",
    "WACCResult",
    "CountryDefaults",
    "DEFAULTS_2026",
    "relever_beta",
    "compute_wacc",
    "wacc_from_defaults",
]
