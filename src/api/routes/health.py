"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Service liveness probe")
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0", service="latam-valuation-engine")
