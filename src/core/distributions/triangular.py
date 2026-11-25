"""
Probability distributions for Monte Carlo valuation.

Origin: Ported from VBA `Module1.TRIANGULAR()` in
E:/valuationapp/Trascender 2023/PlaneaciónFra CANVAS.xlsm

Why triangular? When valuing early-stage SMEs, you rarely have enough
historical data for a normal distribution. Triangular captures three
realistic points (pesimista, probable, optimista) that any founder
or analyst can defend in front of an investment committee.

Big 4 / tier-1 consulting routinely uses triangular when normal
is not justifiable. McKinsey valuation handbook, BCG value-creation
framework, and PwC's IFRS 13 fair-value practice notes all mention
triangular as an acceptable distribution when data is sparse.

Vectorized with NumPy so 10,000 Monte Carlo iterations finish in
milliseconds, not seconds.
"""

from __future__ import annotations

import numpy as np
from scipy import stats as scipy_stats
from pydantic import BaseModel, Field, field_validator, model_validator


class TriangularParams(BaseModel):
    """Parameters for a triangular distribution.

    Invariant: optimistic >= probable >= pessimistic.
    """

    pessimistic: float = Field(..., description="Lower bound (a)")
    probable: float = Field(..., description="Mode (b)")
    optimistic: float = Field(..., description="Upper bound (c)")

    @field_validator("pessimistic", "optimistic")
    @classmethod
    def _finite(cls, v: float) -> float:
        if not np.isfinite(v):
            raise ValueError("must be finite")
        return float(v)

    @model_validator(mode="after")
    def _order(self) -> "TriangularParams":
        if not (self.pessimistic <= self.probable <= self.optimistic):
            raise ValueError(
                f"order violated: pessimistic({self.pessimistic}) <= "
                f"probable({self.probable}) <= optimistic({self.optimistic})"
            )
        # Allow degenerate distribution (a==b==c) — caller signals "no uncertainty".
        # Returning early in triangular_sample skips sqrt; tests cover both paths.
        return self


def triangular_sample(
    n: int,
    pessimistic: float,
    probable: float,
    optimistic: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Draw `n` samples from a triangular distribution.

    Matches the VBA formula in Module1.bas exactly:
        if R < (b - a) / (c - a):
            X = a + sqrt(R * (c - a) * (b - a))
        else:
            X = c - sqrt((1 - R) * (c - a) * (c - b))

    Vectorized: O(n), no Python loop.
    """
    rng = rng if rng is not None else np.random.default_rng()
    params = TriangularParams(pessimistic=pessimistic, probable=probable, optimistic=optimistic)

    a, b, c = params.pessimistic, params.probable, params.optimistic

    # Degenerate distribution (a == b == c): every draw is the constant value.
    if a == c:
        return np.full(n, a, dtype=float)

    u = rng.random(n)

    # CDF threshold (probable quantile within the triangle)
    f_b = (b - a) / (c - a)

    # Both branches computed for every sample, then selected via mask.
    # Faster than looping and avoids branch prediction costs.
    lower = a + np.sqrt(u * (c - a) * (b - a))
    upper = c - np.sqrt((1.0 - u) * (c - a) * (c - b))
    samples = np.where(u < f_b, lower, upper)

    return samples


def triangular_mean(pessimistic: float, probable: float, optimistic: float) -> float:
    """Analytical mean of triangular distribution: (a + b + c) / 3."""
    return (pessimistic + probable + optimistic) / 3.0


def triangular_variance(pessimistic: float, probable: float, optimistic: float) -> float:
    """Analytical variance of triangular distribution."""
    a, b, c = pessimistic, probable, optimistic
    return (a**2 + b**2 + c**2 - a * b - a * c - b * c) / 18.0


def triangular_cdf(x: float | np.ndarray, pessimistic: float, probable: float, optimistic: float) -> float | np.ndarray:
    """CDF of the triangular distribution.

    Useful for probability-of-success statements like
    P(VPN > 0) or P(TIR > WACC).
    """
    return scipy_stats.triang.cdf(
        x,
        c=(probable - pessimistic) / (optimistic - pessimistic),
        loc=pessimistic,
        scale=optimistic - pessimistic,
    )


def triangular_ppf(q: float | np.ndarray, pessimistic: float, probable: float, optimistic: float) -> float | np.ndarray:
    """Inverse CDF (quantile function). For VaR/CVaR style reporting."""
    return scipy_stats.triang.ppf(
        q,
        c=(probable - pessimistic) / (optimistic - pessimistic),
        loc=pessimistic,
        scale=optimistic - pessimistic,
    )


def triangular_summary(pessimistic: float, probable: float, optimistic: float) -> dict:
    """Return a dict with mean, std, var and key quantiles — used in API responses."""
    return {
        "mean": triangular_mean(pessimistic, probable, optimistic),
        "std": np.sqrt(triangular_variance(pessimistic, probable, optimistic)),
        "var": triangular_variance(pessimistic, probable, optimistic),
        "p05": float(triangular_ppf(0.05, pessimistic, probable, optimistic)),
        "p50": float(triangular_ppf(0.50, pessimistic, probable, optimistic)),
        "p95": float(triangular_ppf(0.95, pessimistic, probable, optimistic)),
    }


__all__ = [
    "TriangularParams",
    "triangular_sample",
    "triangular_mean",
    "triangular_variance",
    "triangular_cdf",
    "triangular_ppf",
    "triangular_summary",
]
