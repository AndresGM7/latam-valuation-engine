"""Pydantic schemas for the latam-valuation-engine API."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.macro.data import Country as MacroCountry
from src.core.valuation.wacc import Country as WACCCountry

# Use WACCCountry as the canonical Country enum (re-exported)
Country = WACCCountry


class DCFRequest(BaseModel):
    """Request body for POST /api/v1/valuation/dcf."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "country": "CO",
                "flujos_base": [50, 70, 95, 120, 150],
                "inversion_inicial": 300.0,
                "beta_unlevered": 1.2,
                "debt_to_total_capital_pct": 30.0,
                "n_iterations": 10_000,
                "growth_revenue_pesimista": -5.0,
                "growth_revenue_probable": 5.0,
                "growth_revenue_optimista": 20.0,
            }
        }
    )

    country: Country = Field(..., description="CO, AR, or US")
    flujos_base: list[float] = Field(
        ..., min_length=1, max_length=20,
        description="Baseline free cash flows in millions of local currency. Must be non-empty.",
    )
    inversion_inicial: float = Field(0.0, ge=0, description="Initial investment (same unit as flujos_base)")
    beta_unlevered: float = Field(1.0, ge=0.1, le=3.0, description="Industry beta (unlevered)")
    debt_to_total_capital_pct: float = Field(
        30.0, ge=0, le=100,
        description="Target D/(D+E) capital structure",
    )
    n_iterations: int = Field(10_000, ge=100, le=1_000_000)
    growth_revenue_pesimista: float = Field(-5.0, description="Revenue growth, pessimistic %")
    growth_revenue_probable: float = Field(5.0, description="Revenue growth, probable %")
    growth_revenue_optimista: float = Field(20.0, description="Revenue growth, optimistic %")
    growth_costs_pesimista: float = Field(2.0)
    growth_costs_probable: float = Field(4.0)
    growth_costs_optimista: float = Field(10.0)
    seed: int | None = Field(42, description="Random seed for reproducibility")

    @field_validator("flujos_base")
    @classmethod
    def _no_all_zero(cls, v: list[float]) -> list[float]:
        if all(x == 0 for x in v):
            raise ValueError("flujos_base cannot be all zeros")
        return v


class DCFResponse(BaseModel):
    """Response body for POST /api/v1/valuation/dcf."""

    country: Country
    flujos_base: list[float]
    wacc_pct: float
    cost_of_equity_pct: float
    vpn_mean: float
    vpn_std: float
    vpn_p05: float
    vpn_p50: float
    vpn_p95: float
    prob_vpn_positivo: float
    prob_tir_supera_wacc: float
    tir_proyecto_mean: float
    tir_inversionista_mean: float
    n_iterations: int


class WACCRequest(BaseModel):
    """Request body for POST /api/v1/valuation/wacc."""

    country: Country
    beta_unlevered: float = Field(1.0, ge=0.1, le=3.0)
    debt_to_total_capital_pct: float = Field(30.0, ge=0, le=100)


class WACCResponse(BaseModel):
    """Response body for POST /api/v1/valuation/wacc."""

    country: Country
    cost_of_equity_pct: float
    cost_of_debt_after_tax_pct: float
    wacc_pct: float
    country_risk_premium_applied_pct: float
    components: dict


class MacroResponse(BaseModel):
    """Response body for GET /api/v1/valuation/macro/{country}."""

    country: MacroCountry
    as_of: date
    inflation_yoy_pct: float
    inflation_expectations_1y_pct: float
    inflation_expectations_2y_pct: float
    reference_rate_pct: float
    embi_spread_bps: float
    country_risk_premium_pct: float
    equity_risk_premium_pct: float
    fx_rate_to_usd: float
    fx_volatility_30d_pct: float
    unemployment_pct: float
    gdp_growth_yoy_pct: float
    min_wage_local: float
    tax_rate_corp_pct: float
    debt_to_gdp_pct: float
    source: str


class HealthResponse(BaseModel):
    """Response body for GET /api/v1/health."""

    status: str = "ok"
    version: str
    service: str


class EMBIResponse(BaseModel):
    """Response body for GET /api/v1/valuation/embi/{country}."""

    country: str
    as_of: date
    latest_spread_pct: float
    window_days: int
    moving_average_spread_pct: Optional[float]
    std_window_pct: Optional[float]
    dataset_latest_date: date
    source: str


__all__ = [
    "Country",
    "DCFRequest",
    "DCFResponse",
    "WACCRequest",
    "WACCResponse",
    "MacroResponse",
    "HealthResponse",
]
