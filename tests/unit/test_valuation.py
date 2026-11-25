"""Unit tests for the Monte Carlo DCF engine."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.valuation import MonteCarloConfig, run_monte_carlo


class TestMonteCarloBasic:
    def test_returns_correct_n_samples(self):
        flujos = np.array([50.0, 70.0, 95.0, 120.0, 150.0])
        cfg = MonteCarloConfig(n_iterations=1000, horizon_years=5, seed=42)
        result = run_monte_carlo(flujos, cfg)
        assert result.vpn_samples.shape == (1000,)
        assert result.tir_proy_samples.shape == (1000,)
        assert result.tir_inv_samples.shape == (1000,)

    def test_deterministic_with_same_seed(self):
        flujos = np.array([50.0, 70.0, 95.0, 120.0, 150.0])
        cfg1 = MonteCarloConfig(n_iterations=2000, horizon_years=5, seed=42)
        cfg2 = MonteCarloConfig(n_iterations=2000, horizon_years=5, seed=42)
        r1 = run_monte_carlo(flujos, cfg1)
        r2 = run_monte_carlo(flujos, cfg2)
        np.testing.assert_array_equal(r1.vpn_samples, r2.vpn_samples)

    def test_different_seeds_produce_different_results(self):
        flujos = np.array([50.0, 70.0, 95.0, 120.0, 150.0])
        r1 = run_monte_carlo(flujos, MonteCarloConfig(n_iterations=1000, seed=1))
        r2 = run_monte_carlo(flujos, MonteCarloConfig(n_iterations=1000, seed=2))
        assert not np.array_equal(r1.vpn_samples, r2.vpn_samples)


class TestMonteCarloBehavior:
    def test_high_investment_low_prob_success(self):
        """Massive investment relative to flujos should give low P(VPN>0)."""
        flujos = np.array([10.0, 10.0, 10.0, 10.0, 10.0])
        cfg = MonteCarloConfig(n_iterations=5000, wacc_pct=20.0, inversion_inicial=1000.0, seed=42)
        result = run_monte_carlo(flujos, cfg)
        assert result.prob_exito_vpn_positivo() < 0.05

    def test_low_investment_high_prob_success(self):
        """Tiny investment vs large flujos should give P(VPN>0) close to 1."""
        flujos = np.array([100.0, 200.0, 300.0, 400.0, 500.0])
        cfg = MonteCarloConfig(n_iterations=5000, wacc_pct=5.0, inversion_inicial=10.0, seed=42)
        result = run_monte_carlo(flujos, cfg)
        assert result.prob_exito_vpn_positivo() > 0.95

    def test_zero_inversion_is_pure_dcf(self):
        flujos = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
        cfg_no_inv = MonteCarloConfig(n_iterations=2000, wacc_pct=10.0, inversion_inicial=0.0, seed=42)
        cfg_big_inv = MonteCarloConfig(n_iterations=2000, wacc_pct=10.0, inversion_inicial=500.0, seed=42)
        r_no = run_monte_carlo(flujos, cfg_no_inv)
        r_big = run_monte_carlo(flujos, cfg_big_inv)
        assert r_no.vpn_mean > r_big.vpn_mean
        assert r_no.vpn_mean - r_big.vpn_mean == pytest.approx(500.0, abs=0.01)


class TestMonteCarloPerformance:
    def test_10k_iterations_under_one_second(self):
        """Smoke test that vectorized impl is fast enough for an API."""
        import time
        flujos = np.array([50.0, 70.0, 95.0, 120.0, 150.0])
        cfg = MonteCarloConfig(n_iterations=10_000, seed=42)
        t0 = time.perf_counter()
        run_monte_carlo(flujos, cfg)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0, f"Too slow: {elapsed*1000:.0f}ms"


class TestMonteCarloValidation:
    def test_rejects_mismatched_horizon(self):
        flujos = np.array([50.0, 70.0])  # only 2 elements
        cfg = MonteCarloConfig(n_iterations=100, horizon_years=5, seed=42)
        with pytest.raises(ValueError, match="horizon_years"):
            run_monte_carlo(flujos, cfg)


class TestSummary:
    def test_summary_has_expected_keys(self):
        flujos = np.array([50.0, 70.0, 95.0, 120.0, 150.0])
        cfg = MonteCarloConfig(n_iterations=5000, wacc_pct=15.0, inversion_inicial=300.0, seed=42)
        result = run_monte_carlo(flujos, cfg)
        s = result.summary(wacc_pct=15.0)
        assert "vpn" in s
        assert "tir_proyecto" in s
        assert "tir_inversionista" in s
        assert "prob_supera_wacc" in s["tir_proyecto"]
