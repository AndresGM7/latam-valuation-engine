"""Tests for DCF extensions (two-stage, normalized TV)."""

from __future__ import annotations

import pytest

from src.core.valuation.dcf_extensions import (
    DCFResult,
    dcf_valuation,
    discount_cash_flows,
    gordon_growth_terminal_value,
    terminal_value_two_stage,
    terminal_value_with_normalization,
)


class TestGordonGrowth:
    def test_basic(self):
        # If FCF = 100, g=3%, WACC=10%:
        # TV = 100 * 1.03 / (0.10 - 0.03) = 1471.43
        tv = gordon_growth_terminal_value(100.0, 3.0, 10.0)
        assert tv == pytest.approx(1471.43, abs=0.5)

    def test_invalid_wacc_le_growth_raises(self):
        with pytest.raises(ValueError):
            gordon_growth_terminal_value(100.0, 8.0, 5.0)


class TestTerminalValueNormalization:
    def test_average_used(self):
        # Use average of [100, 110] = 105
        tv = terminal_value_with_normalization([100.0, 110.0], 3.0, 10.0)
        expected = 105 * 1.03 / 0.07  # ~1545
        assert tv == pytest.approx(expected, rel=1e-3)

    def test_three_year_average(self):
        tv = terminal_value_with_normalization([80, 100, 120], 3.0, 10.0)
        # average = 100, TV = 100 * 1.03 / 0.07 = 1471.43
        assert tv == pytest.approx(1471.43, abs=0.5)


class TestTwoStageTerminalValue:
    def test_uses_only_positive_fcfs(self):
        # FCFs: [-50, -30, 100, 110, 121] — first two negative
        # Average of positives: (100+110+121)/3 = 110.33
        tv = terminal_value_two_stage([-50, -30, 100, 110, 121], wacc_pct=10.0, terminal_growth_pct=3.0)
        expected = 110.33 * 1.03 / 0.07  # ~1623
        assert tv == pytest.approx(expected, rel=1e-2)

    def test_all_negative_raises(self):
        with pytest.raises(ValueError):
            terminal_value_two_stage([-100, -50, -20], 10.0, 3.0)


class TestDiscountCashFlows:
    def test_sum_of_discounted(self):
        # FCF [100, 100, 100], WACC=10%
        pv = discount_cash_flows([100, 100, 100], 10.0)
        expected = 100/1.1 + 100/1.21 + 100/1.331  # ~248.69
        assert pv == pytest.approx(expected, rel=1e-3)

    def test_with_initial_investment(self):
        pv = discount_cash_flows([100, 100, 100], 10.0, initial_investment=200.0)
        assert pv == pytest.approx(248.69 - 200, abs=1)


class TestDCFValuationAutoMethod:
    def test_auto_picks_gordon_for_stable_positive(self):
        # All positive, low variance
        result = dcf_valuation(
            fcf_explicit=[100, 110, 121, 133, 146],
            wacc_pct=10.0, terminal_growth_pct=3.0, net_debt=0.0,
        )
        assert result.method == "gordon_growth"
        assert result.enterprise_value > 0

    def test_auto_picks_normalized_for_cyclical(self):
        # High variance
        result = dcf_valuation(
            fcf_explicit=[50, 200, 80, 220, 100],
            wacc_pct=10.0, terminal_growth_pct=3.0, net_debt=0.0,
        )
        assert result.method == "normalized"
        assert result.enterprise_value > 0

    def test_auto_picks_two_stage_for_capex_heavy(self):
        # Negative FCFs (capex year 1-2)
        result = dcf_valuation(
            fcf_explicit=[-500, -300, 100, 200, 300],
            wacc_pct=10.0, terminal_growth_pct=3.0, net_debt=1000.0,
        )
        assert result.method == "two_stage"
        assert result.enterprise_value > 0

    def test_explicit_method_override(self):
        result = dcf_valuation(
            fcf_explicit=[-500, -300, 100, 200, 300],
            wacc_pct=10.0, terminal_growth_pct=3.0, net_debt=1000.0,
            method="gordon_growth",
        )
        assert result.method == "gordon_growth"

    def test_net_debt_subtracted(self):
        result = dcf_valuation(
            fcf_explicit=[100, 110, 121, 133, 146],
            wacc_pct=10.0, terminal_growth_pct=3.0, net_debt=500.0,
        )
        assert result.equity_value == pytest.approx(result.enterprise_value - 500.0, abs=0.5)
