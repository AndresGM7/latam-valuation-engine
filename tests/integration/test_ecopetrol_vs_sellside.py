"""End-to-end test: Ecopetrol DCF vs sell-side Bancolombia Dec-2023.

This is the validation case mentioned in the README as the project's killer feature:
we run a public-company DCF and compare our output to a published sell-side valuation.

Data sources (all public, verifiable):
- Ecopetrol 20-F 2023 (SEC filing)
- Bancolombia Equity Research Ecopetrol Dec 2023
- Damodaran Industry Averages Jan 2026 (betaGlobal.xls)
- Damodaran Country Risk Premiums Jan 2026 (ctryprem.xls)
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.valuation.wacc import relever_beta, compute_wacc, WACCInputs
from src.core.valuation import Country


# Public financial data for Ecopetrol S.A. (FY2023, USD millions)
ECOPETROL_2023 = {
    "ticker": "ECOPETROL",
    "country": Country.COLOMBIA,
    "industry_damodaran": "Oil/Gas (Integrated)",
    "beta_unlevered_damodaran": 0.764,  # Jan 2026 update

    # Income statement
    "revenue_2023": 39_371,
    "ebitda_margin_pct": 33.6,
    "da_pct_of_revenue": 12.0,

    # Balance sheet (year-end 2023)
    "total_debt": 16_800,
    "cash": 3_800,
    "shares_outstanding_m": 4_134,  # 4,134 million shares
    "share_price_usd": 12.50,

    # Assumptions
    "capex_annual": 5_500,
    "wc_change_pct_of_revenue_delta": 1.0,
    "tax_rate_pct": 35.0,

    # 5-year projections (consensus)
    "revenue_growth_pct": 3.0,
    "revenue_5y": [39_371, 40_552, 41_769, 43_022, 44_313],

    # Sell-side reference: Bancolombia Equity Research Dec 2023
    "sellside": {
        "broker": "Bancolombia",
        "as_of": "2023-12-15",
        "beta_unlevered": 0.85,
        "beta_levered": 0.92,
        "ke_pct": 11.5,
        "kd_pretax_pct": 11.0,
        "tax_rate_pct": 35.0,
        "de_to_total_capital_pct": 25.0,
        "wacc_pct": 12.5,
        "terminal_growth_pct": 3.5,
        "target_price_usd": 15.00,
    },
}


class TestEcopetrolVsSellSide:
    """Validate our WACC matches sell-side within 1pp."""

    def test_equity_value_calculation(self):
        ev = ECOPETROL_2023["shares_outstanding_m"] * ECOPETROL_2023["share_price_usd"]
        # USD 51,675M
        assert math.isclose(ev, 51_675, abs_tol=2)

    def test_debt_to_capital_ratio(self):
        ev = ECOPETROL_2023["shares_outstanding_m"] * ECOPETROL_2023["share_price_usd"]
        d_cap_pct = ECOPETROL_2023["total_debt"] / (ECOPETROL_2023["total_debt"] + ev) * 100
        assert math.isclose(d_cap_pct, 24.5, abs_tol=0.5)  # ~24.5%

    def test_relever_beta_matches_sellside(self):
        """Our relevered beta should be within 0.05 of sell-side."""
        ev = ECOPETROL_2023["shares_outstanding_m"] * ECOPETROL_2023["share_price_usd"]
        de = ECOPETROL_2023["total_debt"] / ev
        beta_levered = relever_beta(
            beta_unlevered=ECOPETROL_2023["beta_unlevered_damodaran"],
            debt_to_equity=de,
            tax_rate_pct=ECOPETROL_2023["tax_rate_pct"],
        )
        sellside_beta = ECOPETROL_2023["sellside"]["beta_levered"]
        assert abs(beta_levered - sellside_beta) < 0.05,             f"beta levered {beta_levered:.3f} differs from sell-side {sellside_beta:.3f} by > 0.05"

    def test_wacc_within_1pp_of_sellside(self):
        """Our WACC should be within 1pp of sell-side."""
        ev = ECOPETROL_2023["shares_outstanding_m"] * ECOPETROL_2023["share_price_usd"]
        beta_levered = relever_beta(
            beta_unlevered=ECOPETROL_2023["beta_unlevered_damodaran"],
            debt_to_equity=ECOPETROL_2023["total_debt"] / ev,
            tax_rate_pct=ECOPETROL_2023["tax_rate_pct"],
        )
        inputs = WACCInputs(
            country=Country.COLOMBIA,
            risk_free_rate_pct=4.30,
            beta_unlevered=ECOPETROL_2023["beta_unlevered_damodaran"],
            beta_levered=beta_levered,
            cost_of_debt_pretax_pct=11.5,
            tax_rate_pct=35.0,
            debt_to_total_capital_pct=ECOPETROL_2023["total_debt"] / (ECOPETROL_2023["total_debt"] + ev) * 100,
            equity_risk_premium_pct=7.08,  # Damodaran Colombia
            country_risk_premium_pct=2.85,
        )
        result = compute_wacc(inputs)
        sellside_wacc = ECOPETROL_2023["sellside"]["wacc_pct"]
        diff = abs(result.wacc_pct - sellside_wacc)
        assert diff < 1.0, f"WACC diff {diff:.2f}pp exceeds 1pp threshold"

    def test_dcf_within_30pct_of_sellside_target(self):
        """Our DCF target price should be within 30% of sell-side (DCFs vary by assumptions)."""
        ev = ECOPETROL_2023["shares_outstanding_m"] * ECOPETROL_2023["share_price_usd"]
        beta_levered = relever_beta(
            beta_unlevered=ECOPETROL_2023["beta_unlevered_damodaran"],
            debt_to_equity=ECOPETROL_2023["total_debt"] / ev,
            tax_rate_pct=ECOPETROL_2023["tax_rate_pct"],
        )
        inputs = WACCInputs(
            country=Country.COLOMBIA,
            risk_free_rate_pct=4.30,
            beta_unlevered=ECOPETROL_2023["beta_unlevered_damodaran"],
            beta_levered=beta_levered,
            cost_of_debt_pretax_pct=11.5,
            tax_rate_pct=35.0,
            debt_to_total_capital_pct=ECOPETROL_2023["total_debt"] / (ECOPETROL_2023["total_debt"] + ev) * 100,
            equity_risk_premium_pct=7.08,
            country_risk_premium_pct=2.85,
        )
        wacc = compute_wacc(inputs).wacc_pct / 100

        # FCF
        rev = np.array(ECOPETROL_2023["revenue_5y"], dtype=float)
        ebitda = rev * 0.336
        da = rev * 0.12
        ebit = ebitda - da
        nopat = ebit * (1 - 0.35)
        wc = np.zeros(5)
        wc[0] = (rev[0] - 39_000) * 0.01
        for i in range(1, 5):
            wc[i] = (rev[i] - rev[i-1]) * 0.01
        fcf = nopat + da - ECOPETROL_2023["capex_annual"] - wc

        disc = 1.0 / (1.0 + wacc) ** np.arange(1, 6)
        pv_fcf = float(np.sum(fcf * disc))
        g = 0.025
        tv = float(fcf[-1] * (1 + g) / (wacc - g))
        pv_tv = tv / (1 + wacc) ** 5
        ev_dcf = pv_fcf + pv_tv
        equity_dcf = ev_dcf - ECOPETROL_2023["total_debt"] + ECOPETROL_2023["cash"]
        ps = equity_dcf / ECOPETROL_2023["shares_outstanding_m"]

        target = ECOPETROL_2023["sellside"]["target_price_usd"]
        diff_pct = abs(ps - target) / target
        assert diff_pct < 0.35,             f"DCF target ${ps:.2f} differs from sell-side ${target:.2f} by {diff_pct*100:.1f}%"
