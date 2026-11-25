"""Unit tests for triangular distribution.

Verifies the Python port matches the VBA `Module1.TRIANGULAR()` formula
exactly, and that statistical properties match theory.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.distributions import (
    TriangularParams,
    triangular_cdf,
    triangular_mean,
    triangular_ppf,
    triangular_sample,
    triangular_summary,
    triangular_variance,
)


class TestTriangularSample:
    def test_returns_correct_size(self):
        rng = np.random.default_rng(42)
        samples = triangular_sample(1000, 0.85, 1.0, 1.30, rng=rng)
        assert samples.shape == (1000,)

    def test_all_samples_within_bounds(self):
        rng = np.random.default_rng(42)
        samples = triangular_sample(50_000, 0.85, 1.0, 1.30, rng=rng)
        assert samples.min() >= 0.85
        assert samples.max() <= 1.30

    def test_vectorized_fast(self):
        """100k iterations must complete in well under a second."""
        rng = np.random.default_rng(42)
        import time
        t0 = time.perf_counter()
        triangular_sample(100_000, 0.85, 1.0, 1.30, rng=rng)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 500, f"Too slow: {elapsed_ms:.0f}ms"

    def test_matches_vba_formula_aggregate(self):
        """Compare 100k-sample mean and variance against the analytical formulas
        (which are derived from the same VBA formula)."""
        a, b, c = 0.85, 1.0, 1.30
        rng = np.random.default_rng(42)
        samples = triangular_sample(100_000, a, b, c, rng=rng)
        np.testing.assert_allclose(samples.mean(), (a + b + c) / 3, atol=0.01)
        expected_var = (a**2 + b**2 + c**2 - a*b - a*c - b*c) / 18.0
        np.testing.assert_allclose(samples.var(), expected_var, atol=0.001)


class TestTriangularMoments:
    def test_mean(self):
        assert triangular_mean(0.85, 1.0, 1.30) == pytest.approx(1.05, rel=1e-9)

    def test_variance(self):
        expected = (0.85**2 + 1.0**2 + 1.30**2 - 0.85*1.0 - 0.85*1.30 - 1.0*1.30) / 18.0
        assert triangular_variance(0.85, 1.0, 1.30) == pytest.approx(expected, rel=1e-9)


class TestTriangularBounds:
    def test_rejects_inverted_bounds(self):
        with pytest.raises(ValueError, match="order violated"):
            TriangularParams(pessimistic=1.0, probable=0.9, optimistic=1.0)

    def test_rejects_equal_bounds(self):
        with pytest.raises(ValueError, match="collapses"):
            TriangularParams(pessimistic=1.0, probable=1.0, optimistic=1.0)


class TestTriangularSummary:
    def test_returns_expected_keys(self):
        s = triangular_summary(0.85, 1.0, 1.30)
        assert set(s.keys()) == {"mean", "std", "var", "p05", "p50", "p95"}

    def test_percentiles_in_bounds(self):
        s = triangular_summary(0.85, 1.0, 1.30)
        assert 0.85 <= s["p05"] <= s["p50"] <= s["p95"] <= 1.30


class TestTriangularCDFPPF:
    def test_cdf_at_lower_bound_is_zero(self):
        cdf_val = triangular_cdf(0.85, 0.85, 1.0, 1.30)
        assert cdf_val == pytest.approx(0.0, abs=1e-9)

    def test_cdf_at_upper_bound_is_one(self):
        cdf_val = triangular_cdf(1.30, 0.85, 1.0, 1.30)
        assert cdf_val == pytest.approx(1.0, abs=1e-9)

    def test_ppf_inverse_of_cdf(self):
        for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
            x = triangular_ppf(q, 0.85, 1.0, 1.30)
            cdf_back = triangular_cdf(x, 0.85, 1.0, 1.30)
            assert cdf_back == pytest.approx(q, abs=1e-9)
