"""Endpoints for the EMBI Latam historical dataset."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Path, Query

from src.api.schemas import EMBIResponse
from src.core.macro.embi import load_embi

router = APIRouter(prefix="/api/v1/valuation", tags=["embi"])


@router.get("/embi/{country}", response_model=EMBIResponse)
def get_embi(
    country: str = Path(..., description="Country name as in dataset (e.g. Colombia, Argentina)"),
    window_days: int = Query(30, ge=1, le=365, description="Moving average window"),
):
    """Return the latest EMBI reading + N-day moving average for a Latam country.

    Data source: BCRD (Banco Central de la República Dominicana), updated daily.
    See: https://www.bancentral.gov.do/a/d/2585-entorno-internacional
    """
    ds = load_embi()
    latest = ds.latest(country)
    if latest is None:
        raise HTTPException(
            status_code=404,
            detail=f"Country {country!r} not found. Available: {ds.countries}",
        )
    ma = ds.moving_average(country, window_days=window_days)
    return EMBIResponse(
        country=country,
        as_of=latest.as_of,
        latest_spread_pct=latest.spread_pct,
        window_days=window_days,
        moving_average_spread_pct=ma.spread_pct if ma else None,
        std_window_pct=ma.std_30d_pct if ma else None,
        dataset_latest_date=ds.latest_date,
        source="BCRD EMBI Global Diversified Subindices (daily)",
    )


@router.get("/embi")
def list_countries():
    """List all available Latam countries in the EMBI dataset."""
    ds = load_embi()
    return {
        "countries": ds.countries,
        "dataset_latest_date": ds.latest_date,
        "source": "BCRD EMBI Global Diversified Subindices",
    }
