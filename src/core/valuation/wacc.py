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

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Country(str, Enum):
    COLOMBIA = "CO"
    ARGENTINA = "AR"
    MEXICO = "MX"
    CHILE = "CL"
    BRAZIL = "BR"
    PERU = "PE"
    UNITED_STATES = "US"  # baseline; no country risk premium


class WACCInputs(BaseModel):
    """Inputs to compute WACC.

    Two ways to specify country risk:

    Mode 1 (recommended for non-AR, non-Venezuela Latam):
        Set `equity_risk_premium_pct` to Damodaran TOTAL ERP (already includes CRP).
        Set `country_risk_premium_pct = 0`.

    Mode 2 (for Argentina, Venezuela, or hyperinflationary economies):
        Set `mature_erp_pct = 5.5` (Damodaran mature market premium).
        Set `country_risk_premium_pct = EMBI/BCRD sovereign spread`.
        Set `fx_risk_premium_pct = expected depreciation vs inflation differential`.
        Leave `equity_risk_premium_pct = None` to use the decomposable components.

    Damodaran's "total ERP" already includes CRP for the country.
    Adding CRP again would double-count. This model lets you choose either path.
    """

    country: Country
    risk_free_rate_pct: float = Field(..., ge=0, le=30, description="US 10Y Treasury or local risk-free proxy")

    # Path A: Damodaran total ERP (mature + CRP combined). Use this OR the decomposable components below.
    equity_risk_premium_pct: float | None = Field(
        None, ge=0, le=30,
        description="Damodaran TOTAL ERP for the country (mature + CRP). Use ONLY this if you don't decompose."
    )

    # Path B: Decomposable components (for AR, VE, or any country with FX risk)
    mature_erp_pct: float | None = Field(None, ge=0, le=20, description="Mature market ERP (Damodaran: 5.5% for US)")
    country_risk_premium_pct: float = Field(0.0, ge=0, le=30, description="EMBI spread or sovereign CDS")
    fx_risk_premium_pct: float = Field(0.0, ge=0, le=30, description="Expected depreciation vs inflation differential (AR only)")

    beta_unlevered: float = Field(..., ge=0.1, le=3.0, description="Industry beta from Damodaran")
    debt_to_total_capital_pct: float = Field(..., ge=0, le=100, description="Target D/(D+E)")
    cost_of_debt_pretax_pct: float = Field(..., ge=0, le=50, description="Local currency borrowing rate")
    tax_rate_pct: float = Field(..., ge=0, le=50, description="Effective corporate tax rate")

    size_premium_pct: float = Field(0.0, ge=0, le=10, description="Size premium for small caps (Duff & Phelps)")

    @model_validator(mode="after")
    def _validate_erp_path(self) -> "WACCInputs":
        """Either equity_risk_premium_pct OR mature_erp_pct must be set, not both."""
        if self.equity_risk_premium_pct is None and self.mature_erp_pct is None:
            raise ValueError(
                "Must provide either `equity_risk_premium_pct` (Damodaran total ERP) "
                "OR `mature_erp_pct` (decomposable). See docstring."
            )
        if self.equity_risk_premium_pct is not None and self.mature_erp_pct is not None:
            raise ValueError(
                "Provide either `equity_risk_premium_pct` OR `mature_erp_pct`, not both. "
                "Using both double-counts CRP."
            )
        return self

    @field_validator("risk_free_rate_pct", "country_risk_premium_pct", "fx_risk_premium_pct",
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

    Cost of equity formula (CAPM with country + FX risk):
        Ke = Rf + β_levered × ERP_effective + CRP + FX_risk + size_premium

    Where ERP_effective is one of:
        Path A: `equity_risk_premium_pct` (Damodaran total, includes CRP)
        Path B: `mature_erp_pct` (just the mature market portion; CRP added separately)

    Cost of debt and WACC follow the standard formula.
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

    # Decide which ERP path to use
    if inputs.equity_risk_premium_pct is not None:
        # Path A: Damodaran total ERP (already includes CRP). Do NOT add CRP again.
        erp_effective = inputs.equity_risk_premium_pct
        crp_applied = 0.0  # already inside ERP
    else:
        # Path B: mature ERP + CRP + FX risk (decomposable for AR, VE)
        erp_effective = inputs.mature_erp_pct or 0.0
        crp_applied = inputs.country_risk_premium_pct

    cost_of_equity = (
        inputs.risk_free_rate_pct
        + beta_levered * erp_effective
        + crp_applied
        + inputs.fx_risk_premium_pct
        + inputs.size_premium_pct
    )

    cost_of_debt_after_tax = inputs.cost_of_debt_pretax_pct * (1.0 - inputs.tax_rate_pct / 100.0)

    wacc = cost_of_equity * e_over_v + cost_of_debt_after_tax * d_over_v

    return WACCResult(
        cost_of_equity_pct=cost_of_equity,
        cost_of_debt_after_tax_pct=cost_of_debt_after_tax,
        wacc_pct=wacc,
        country_risk_premium_applied_pct=crp_applied + inputs.fx_risk_premium_pct,
        components={
            "rf": inputs.risk_free_rate_pct,
            "beta_levered": beta_levered,
            "erp_effective": erp_effective,
            "crp": crp_applied,
            "fx_risk": inputs.fx_risk_premium_pct,
            "size_premium": inputs.size_premium_pct,
            "kd_pretax": inputs.cost_of_debt_pretax_pct,
            "kd_after_tax": cost_of_debt_after_tax,
            "D_over_V": d_over_v,
            "E_over_V": e_over_v,
            "erp_path": "A_total_Damodaran" if inputs.equity_risk_premium_pct is not None else "B_decomposable",
        },
    )


# ------------------------------------------------------------
# Convenience presets calibrated to Damodaran Jan 2026 + World Bank 2025.
# Source: https://pages.stern.nyu.edu/~adamodar/pc/datasets/ctryprem.xls
#         https://pages.stern.nyu.edu/~adamodar/pc/datasets/betaGlobal.xls
#         https://api.worldbank.org/v2/country/{CO,AR}/indicator/
# Updated: 2026-01-15 by Hermes Agent
# ------------------------------------------------------------


@dataclass
class CountryDefaults:
    """Default country-level inputs for WACC. Update these as Banrep/SFC publish new data."""

    country: Country
    risk_free_rate_pct: float  # US 10Y sovereign bond yield (USD-denominated for AR)
    equity_risk_premium_pct: float  # Damodaran total ERP for the country (mature + CRP)
    country_risk_premium_pct: float  # Damodaran CRP
    cost_of_debt_pretax_pct: float  # Avg commercial bank lending rate
    tax_rate_pct: float


# 2026-Q1 calibration from Damodaran + World Bank.
DEFAULTS_2026 = {
    Country.COLOMBIA: CountryDefaults(
        country=Country.COLOMBIA,
        risk_free_rate_pct=4.30,        # US 10Y Treasury proxy
        equity_risk_premium_pct=7.08,   # Damodaran Jan 2026 (Baa3 rated, total ERP)
        country_risk_premium_pct=2.85,  # Damodaran Jan 2026 (Colombia CRP)
        cost_of_debt_pretax_pct=17.40,  # Tasa Bancos promedio SFC (placeholder - verify)
        tax_rate_pct=35.0,              # Tarifa nominal Colombia 2024+
    ),
    Country.ARGENTINA: CountryDefaults(
        country=Country.ARGENTINA,
        risk_free_rate_pct=4.30,        # US 10Y proxy (Argentina no tiene 10Y USD líquido)
        equity_risk_premium_pct=13.94,  # Damodaran Jan 2026 (Caa1 rated, total ERP)
        country_risk_premium_pct=9.71,  # Damodaran Jan 2026 (Argentina CRP)
        cost_of_debt_pretax_pct=45.00,  # BADLAR + spread (placeholder - verify post-devaluación)
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
    Country.MEXICO: CountryDefaults(
        country=Country.MEXICO,
        risk_free_rate_pct=4.30,        # US 10Y proxy (MX sovereign curve is USD-denominated)
        equity_risk_premium_pct=6.10,   # Damodaran Jan 2026 (Baa2 rated, total ERP)
        country_risk_premium_pct=1.84,  # Damodaran Jan 2026 (Mexico CRP)
        cost_of_debt_pretax_pct=12.50,  # TIIE + spread (placeholder - verify with Banxico)
        tax_rate_pct=30.0,              # ISR nominal Mexico
    ),
    Country.CHILE: CountryDefaults(
        country=Country.CHILE,
        risk_free_rate_pct=4.30,
        equity_risk_premium_pct=6.06,   # Damodaran Jan 2026 (A rated, total ERP)
        country_risk_premium_pct=1.10,  # Damodaran Jan 2026 (Chile CRP)
        cost_of_debt_pretax_pct=10.50,  # BCCh reference rate
        tax_rate_pct=27.0,              # Impuesto a la renta Chile
    ),
    Country.BRAZIL: CountryDefaults(
        country=Country.BRAZIL,
        risk_free_rate_pct=4.30,
        equity_risk_premium_pct=8.85,   # Damodaran Jan 2026 (Ba2 rated, total ERP)
        country_risk_premium_pct=3.10,  # Damodaran Jan 2026 (Brazil CRP)
        cost_of_debt_pretax_pct=15.50,  # CDI + spread
        tax_rate_pct=34.0,              # IRPJ + CSLL
    ),
    Country.PERU: CountryDefaults(
        country=Country.PERU,
        risk_free_rate_pct=4.30,
        equity_risk_premium_pct=6.85,   # Damodaran Jan 2026 (A3 rated, total ERP)
        country_risk_premium_pct=1.74,  # Damodaran Jan 2026 (Peru CRP)
        cost_of_debt_pretax_pct=10.80,
        tax_rate_pct=29.5,
    ),
}


def wacc_from_defaults(
    country: Country,
    beta_unlevered: float = 1.0,
    debt_to_total_capital_pct: float = 30.0,
) -> WACCResult:
    """Compute WACC using calibrated defaults + user-provided beta and capital structure.

    This is the convenience function most API calls will use.
    Uses Path A: Damodaran total ERP (which already includes CRP).
    """
    defaults = DEFAULTS_2026[country]
    inputs = WACCInputs(
        country=country,
        risk_free_rate_pct=defaults.risk_free_rate_pct,
        equity_risk_premium_pct=defaults.equity_risk_premium_pct,
        country_risk_premium_pct=0.0,  # Path A: CRP already inside equity_risk_premium_pct
        beta_unlevered=beta_unlevered,
        debt_to_total_capital_pct=debt_to_total_capital_pct,
        cost_of_debt_pretax_pct=defaults.cost_of_debt_pretax_pct,
        tax_rate_pct=defaults.tax_rate_pct,
    )
    return compute_wacc(inputs)


def wacc_decomposable(
    country: Country,
    mature_erp_pct: float,
    country_risk_premium_pct: float,
    fx_risk_premium_pct: float = 0.0,
    beta_unlevered: float = 1.0,
    debt_to_total_capital_pct: float = 30.0,
    risk_free_rate_pct: float | None = None,
    cost_of_debt_pretax_pct: float | None = None,
    tax_rate_pct: float | None = None,
) -> WACCResult:
    """Compute WACC using decomposable components (Path B).

    Use this for hyperinflationary economies (Argentina, Venezuela, Turkey, Nigeria)
    where the cost of equity must be decomposed into mature-market ERP + sovereign CRP
    + FX risk premium. The defaults are used for any unspecified parameter.
    """
    defaults = DEFAULTS_2026[country]
    inputs = WACCInputs(
        country=country,
        risk_free_rate_pct=risk_free_rate_pct if risk_free_rate_pct is not None else defaults.risk_free_rate_pct,
        mature_erp_pct=mature_erp_pct,
        country_risk_premium_pct=country_risk_premium_pct,
        fx_risk_premium_pct=fx_risk_premium_pct,
        beta_unlevered=beta_unlevered,
        debt_to_total_capital_pct=debt_to_total_capital_pct,
        cost_of_debt_pretax_pct=cost_of_debt_pretax_pct if cost_of_debt_pretax_pct is not None else defaults.cost_of_debt_pretax_pct,
        tax_rate_pct=tax_rate_pct if tax_rate_pct is not None else defaults.tax_rate_pct,
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
    "wacc_decomposable",
]
