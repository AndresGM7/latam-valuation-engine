"""Valuation routes: DCF, WACC, macro snapshot."""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException, Path

from src.api.schemas import (
    DCFRequest,
    DCFResponse,
    WACCRequest,
    WACCResponse,
    MacroResponse,
)
from src.core.macro.data import Country as MacroCountry, load_macro
from src.core.valuation.monte_carlo import MonteCarloConfig, run_monte_carlo
from src.core.valuation.wacc import wacc_from_defaults

router = APIRouter(prefix="/api/v1/valuation", tags=["valuation"])


@router.post("/dcf", response_model=DCFResponse, summary="Run a Monte Carlo DCF valuation")
def dcf(req: DCFRequest) -> DCFResponse:
    """Run vectorized Monte Carlo DCF for the given country and cash flows.

    The country-specific WACC (with EMBI sovereign risk premium) is
    applied automatically. Returns mean, percentiles, and probability
    of success (P(VPN > 0), P(TIR > WACC)).
    """
    wacc_result = wacc_from_defaults(
        country=req.country,
        beta_unlevered=req.beta_unlevered,
        debt_to_total_capital_pct=req.debt_to_total_capital_pct,
    )

    flujos = np.array(req.flujos_base, dtype=float)
    if flujos.size == 0:
        raise HTTPException(status_code=422, detail="flujos_base must not be empty")

    cfg = MonteCarloConfig(
        n_iterations=req.n_iterations,
        horizon_years=flujos.size,
        wacc_pct=wacc_result.wacc_pct,
        inversion_inicial=req.inversion_inicial,
        growth_revenue_pesimista=req.growth_revenue_pesimista,
        growth_revenue_probable=req.growth_revenue_probable,
        growth_revenue_optimista=req.growth_revenue_optimista,
        growth_costs_pesimista=req.growth_costs_pesimista,
        growth_costs_probable=req.growth_costs_probable,
        growth_costs_optimista=req.growth_costs_optimista,
        seed=req.seed,
    )

    try:
        result = run_monte_carlo(flujos, cfg)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return DCFResponse(
        country=req.country,
        flujos_base=req.flujos_base,
        wacc_pct=wacc_result.wacc_pct,
        cost_of_equity_pct=wacc_result.cost_of_equity_pct,
        vpn_mean=result.vpn_mean,
        vpn_std=result.vpn_std,
        vpn_p05=result.vpn_p05,
        vpn_p50=result.vpn_p50,
        vpn_p95=result.vpn_p95,
        prob_vpn_positivo=result.prob_exito_vpn_positivo(),
        prob_tir_supera_wacc=result.prob_exito_tir_supera_wacc(wacc_result.wacc_pct),
        tir_proyecto_mean=float(np.mean(result.tir_proy_samples)),
        tir_inversionista_mean=float(np.mean(result.tir_inv_samples)),
        n_iterations=result.n_iterations,
    )


@router.post("/wacc", response_model=WACCResponse, summary="Compute WACC for a country")
def wacc(req: WACCRequest) -> WACCResponse:
    """Compute WACC with country risk premium for the given inputs."""
    result = wacc_from_defaults(
        country=req.country,
        beta_unlevered=req.beta_unlevered,
        debt_to_total_capital_pct=req.debt_to_total_capital_pct,
    )
    return WACCResponse(
        country=req.country,
        cost_of_equity_pct=result.cost_of_equity_pct,
        cost_of_debt_after_tax_pct=result.cost_of_debt_after_tax_pct,
        wacc_pct=result.wacc_pct,
        country_risk_premium_applied_pct=result.country_risk_premium_applied_pct,
        components=result.components,
    )


@router.get(
    "/macro/{country}",
    response_model=MacroResponse,
    summary="Latest macro snapshot for a country",
)
def macro(country: str = Path(..., pattern="^(CO|AR)$")) -> MacroResponse:
    """Return the latest macro snapshot for Colombia or Argentina."""
    try:
        macro_country = MacroCountry(country)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        snap = load_macro(macro_country)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return MacroResponse(**snap.model_dump())
