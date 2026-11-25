"""Unit tests for WACC with country risk premium."""

from __future__ import annotations

import pytest

from src.core.valuation.wacc import (
    Country,
    relever_beta,
    wacc_from_defaults,
)


class TestWACCRelativity:
    """The killer feature: WACC differs by country risk."""

    def test_argentina_wacc_higher_than_usa(self):
        ar = wacc_from_defaults(Country.ARGENTINA, beta_unlevered=1.0, debt_to_total_capital_pct=30.0)
        us = wacc_from_defaults(Country.UNITED_STATES, beta_unlevered=1.0, debt_to_total_capital_pct=30.0)
        assert ar.wacc_pct > us.wacc_pct, f"AR WACC ({ar.wacc_pct}) should exceed US WACC ({us.wacc_pct})"

    def test_argentina_wacc_higher_than_colombia(self):
        ar = wacc_from_defaults(Country.ARGENTINA, beta_unlevered=1.0, debt_to_total_capital_pct=30.0)
        co = wacc_from_defaults(Country.COLOMBIA, beta_unlevered=1.0, debt_to_total_capital_pct=30.0)
        assert ar.wacc_pct > co.wacc_pct

    def test_colombia_wacc_higher_than_usa(self):
        co = wacc_from_defaults(Country.COLOMBIA, beta_unlevered=1.0, debt_to_total_capital_pct=30.0)
        us = wacc_from_defaults(Country.UNITED_STATES, beta_unlevered=1.0, debt_to_total_capital_pct=30.0)
        assert co.wacc_pct > us.wacc_pct

    def test_country_risk_premium_applied_only_for_latam(self):
        ar = wacc_from_defaults(Country.ARGENTINA)
        us = wacc_from_defaults(Country.UNITED_STATES)
        assert ar.country_risk_premium_applied_pct > 0
        assert us.country_risk_premium_applied_pct == 0


class TestReleverBeta:
    def test_zero_debt_returns_unlevered(self):
        assert relever_beta(beta_unlevered=1.2, debt_to_equity=0.0, tax_rate_pct=30.0) == pytest.approx(1.2)

    def test_higher_leverage_increases_beta(self):
        b_low = relever_beta(1.0, debt_to_equity=0.0, tax_rate_pct=30.0)
        b_high = relever_beta(1.0, debt_to_equity=1.0, tax_rate_pct=30.0)
        assert b_high > b_low

    def test_higher_tax_lowers_levered_beta(self):
        b_low_tax = relever_beta(1.0, debt_to_equity=1.0, tax_rate_pct=0.0)
        b_high_tax = relever_beta(1.0, debt_to_equity=1.0, tax_rate_pct=40.0)
        assert b_high_tax < b_low_tax


class TestWACCComponents:
    def test_wacc_is_between_ke_and_kd(self):
        r = wacc_from_defaults(Country.COLOMBIA, beta_unlevered=1.2, debt_to_total_capital_pct=30.0)
        lo = min(r.cost_of_equity_pct, r.cost_of_debt_after_tax_pct)
        hi = max(r.cost_of_equity_pct, r.cost_of_debt_after_tax_pct)
        assert lo <= r.wacc_pct <= hi

    def test_components_dict_has_required_keys(self):
        r = wacc_from_defaults(Country.COLOMBIA)
        for key in ["rf", "beta_levered", "erp", "crp", "kd_pretax", "kd_after_tax", "D_over_V", "E_over_V"]:
            assert key in r.components
