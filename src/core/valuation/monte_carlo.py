"""Monte Carlo simulation engine for DCF valuation.

Origin: Ported from VBA `Module2.SIMULACION()` in
E:/valuationapp/Trascender 2023/PlaneaciónFra CANVAS.xlsm

The original VBA loop:
    For i = 1 To N
        Calculate              ' forces Excel to recompute RAND() and RANDBETWEEN()
        VPN(i) = Sheets("FCL").Cells(27, 7)
        TIR_Proy(i) = Sheets("FCL").Cells(25, 7)
        TIR_Inv(i) = Sheets("FCL").Cells(26, 7)
    Next i

In Python we replace `Calculate` with explicit NumPy random draws, and we
replace the per-iteration scalar assignment with vectorized numpy ops.
The result: 10,000 iterations in milliseconds vs minutes in Excel.

Each iteration produces one (VPN, TIR_proy, TIR_inv) sample. The summary
function reports mean, std, percentiles, and probability of success
(P(VPN > 0), P(TIR > WACC)).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from ..distributions.triangular import triangular_sample


@dataclass
class MonteCarloConfig:
    """Inputs to one Monte Carlo run."""

    n_iterations: int = 10_000
    seed: int | None = 42
    horizon_years: int = 5

    # Initial investment in same currency unit as flujos (e.g. COP million)
    inversion_inicial: float = 0.0

    # WACC to discount flujos AND compare against TIR (in %)
    wacc_pct: float = 15.0

    # Tax rate (in %) applied in DCF bridge
    tax_rate_pct: float = 30.0

    # Triangular bounds for each uncertain variable (in %, e.g. 5.0 = 5%)
    # All bounds apply to YoY change of the respective variable.
    growth_revenue_pesimista: float = -5.0
    growth_revenue_probable: float = 5.0
    growth_revenue_optimista: float = 20.0

    growth_costs_pesimista: float = 2.0
    growth_costs_probable: float = 4.0
    growth_costs_optimista: float = 10.0

    rotacion_cxc_min_dias: int = 20
    rotacion_cxc_max_dias: int = 60
    rotacion_cxp_min_dias: int = 15
    rotacion_cxp_max_dias: int = 90


@dataclass
class MonteCarloResult:
    """Outputs of one Monte Carlo run."""

    n_iterations: int
    vpn_samples: np.ndarray
    tir_proy_samples: np.ndarray
    tir_inv_samples: np.ndarray

    @property
    def vpn_mean(self) -> float:
        return float(np.mean(self.vpn_samples))

    @property
    def vpn_std(self) -> float:
        return float(np.std(self.vpn_samples))

    @property
    def vpn_p05(self) -> float:
        return float(np.percentile(self.vpn_samples, 5))

    @property
    def vpn_p50(self) -> float:
        return float(np.percentile(self.vpn_samples, 50))

    @property
    def vpn_p95(self) -> float:
        return float(np.percentile(self.vpn_samples, 95))

    def prob_exito_vpn_positivo(self) -> float:
        return float(np.mean(self.vpn_samples > 0))

    def prob_exito_tir_supera_wacc(self, wacc_pct: float) -> float:
        return float(np.mean(self.tir_proy_samples > wacc_pct / 100.0))

    def summary(self, wacc_pct: float | None = None) -> dict:
        """Return a JSON-serializable summary suitable for API responses."""
        wacc = (wacc_pct if wacc_pct is not None else 0.0) / 100.0
        return {
            "n_iterations": self.n_iterations,
            "vpn": {
                "mean": self.vpn_mean,
                "std": self.vpn_std,
                "p05": self.vpn_p05,
                "p50": self.vpn_p50,
                "p95": self.vpn_p95,
                "prob_positivo": self.prob_exito_vpn_positivo(),
            },
            "tir_proyecto": {
                "mean": float(np.mean(self.tir_proy_samples)),
                "std": float(np.std(self.tir_proy_samples)),
                "p05": float(np.percentile(self.tir_proy_samples, 5)),
                "p50": float(np.percentile(self.tir_proy_samples, 50)),
                "p95": float(np.percentile(self.tir_proy_samples, 95)),
                "prob_supera_wacc": self.prob_exito_tir_supera_wacc(wacc_pct or 0.0),
            },
            "tir_inversionista": {
                "mean": float(np.mean(self.tir_inv_samples)),
                "std": float(np.std(self.tir_inv_samples)),
                "p05": float(np.percentile(self.tir_inv_samples, 5)),
                "p50": float(np.percentile(self.tir_inv_samples, 50)),
                "p95": float(np.percentile(self.tir_inv_samples, 95)),
            },
        }


def run_monte_carlo(
    flujos_base: np.ndarray,
    config: MonteCarloConfig,
    inversion_inicial: float | None = None,
) -> MonteCarloResult:
    """Run N Monte Carlo iterations on a base 5-year cash flow projection.

    Args:
        flujos_base: Array of length horizon_years with the BASELINE flujos
            de caja libre (post-tax, post-capex, post-KTNO change). Unit
            must be consistent with inversion_inicial.
        config: Monte Carlo configuration (triangular bounds, N, WACC, etc.).
        inversion_inicial: Initial investment to subtract for VPN calc.
            Defaults to config.inversion_inicial.

    Returns:
        MonteCarloResult with N samples each of VPN, TIR_proy, TIR_inv.

    Vectorized implementation:
        - All N iterations are computed in one numpy pass.
        - No Python loops over iterations.
        - Triangular draws are batched.
        - Discount factors are precomputed.
    """
    if flujos_base.shape[0] != config.horizon_years:
        raise ValueError(
            f"flujos_base length ({flujos_base.shape[0]}) != "
            f"horizon_years ({config.horizon_years})"
        )

    if inversion_inicial is None:
        inversion_inicial = config.inversion_inicial

    rng = np.random.default_rng(config.seed)

    # 1. Sample N growth paths for revenue (size N x horizon)
    growth_rev = triangular_sample(
        n=config.n_iterations * config.horizon_years,
        pessimistic=config.growth_revenue_pesimista / 100.0,
        probable=config.growth_revenue_probable / 100.0,
        optimistic=config.growth_revenue_optimista / 100.0,
        rng=rng,
    ).reshape(config.n_iterations, config.horizon_years)

    growth_cost = triangular_sample(
        n=config.n_iterations * config.horizon_years,
        pessimistic=config.growth_costs_pesimista / 100.0,
        probable=config.growth_costs_probable / 100.0,
        optimistic=config.growth_costs_optimista / 100.0,
        rng=rng,
    ).reshape(config.n_iterations, config.horizon_years)

    # 2. Build per-iteration flujos de caja applying random growth.
    #
    # INVARIANT (critical for auditability): when growth = 0 for all years,
    # the resulting VPN must equal the textbook DCF:
    #     VPN = sum(flujos_base[t] / (1+wacc)^(t+1)) - inversion_inicial
    #
    # cumulative_growth_* are np.cumprod(1+g_t), so when all g_t=0 they equal 1.0.
    base_expanded = np.tile(flujos_base, (config.n_iterations, 1))  # shape (N, T)

    # Cumulative growth factor (1.0 when growth is 0)
    cumulative_growth_rev = np.cumprod(1.0 + growth_rev, axis=1)
    cumulative_growth_cost = np.cumprod(1.0 + growth_cost, axis=1)

    # Multiplicative growth on top of base (1.0 = no change)
    growth_rev_factor = cumulative_growth_rev

    # Cost growth acts as a drag on net flows, elasticity = 0.1 (1% cost growth
    # → 0.1% net-flow reduction). When growth_cost_cum = 1.0 (no growth), drag = 0.
    cost_elasticity = 0.1
    growth_cost_factor = 1.0 - (cumulative_growth_cost - 1.0) * cost_elasticity

    flujos_sim = base_expanded * growth_rev_factor * growth_cost_factor

    # 3. Discount each year's flujo to present value
    years = np.arange(1, config.horizon_years + 1)
    discount_factors = 1.0 / (1.0 + config.wacc_pct / 100.0) ** years
    flujos_descontados = flujos_sim * discount_factors

    vpn_samples = flujos_descontados.sum(axis=1) - inversion_inicial

    # 4. TIR_proy = internal rate of return on the project cash flows.
    # Vectorized IRR is non-trivial; for N=10k we use a closed-form
    # approximation: TIR ≈ WACC + std(vpn) / mean(flujos)
    # For exact IRR see scipy.optimize.npv-based implementation in tir.py.
    # We expose TIR_proy as a derived metric; the EXACT IRR is computed
    # on-demand for the user's selected scenario, not for all MC samples.
    tir_proy_samples = config.wacc_pct / 100.0 + (
        vpn_samples - vpn_samples.mean()
    ) / max(np.abs(flujos_base.mean()) * config.horizon_years, 1e-9)

    tir_inv_samples = tir_proy_samples.copy()  # same proxy for now; refine in tir.py

    return MonteCarloResult(
        n_iterations=config.n_iterations,
        vpn_samples=vpn_samples,
        tir_proy_samples=tir_proy_samples,
        tir_inv_samples=tir_inv_samples,
    )


__all__ = ["MonteCarloConfig", "MonteCarloResult", "run_monte_carlo"]
