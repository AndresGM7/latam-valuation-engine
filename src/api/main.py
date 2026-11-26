"""Main FastAPI application.

Run locally:
    uvicorn src.api.main:app --reload

OpenAPI docs:
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import embi_router, health_router, valuation_router
from src.core.settings import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()

app = FastAPI(
    title="latam-valuation-engine",
    description=(
        "DCF + Monte Carlo + country-specific WACC for Colombia and Argentina. "
        "Built to be the only open-source toolkit that respects EMBI sovereign risk."
    ),
    version="0.1.0",
    contact={
        "name": "Andres Giraldo",
        "url": "https://github.com/AndresGM7/latam-valuation-engine",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "health", "description": "Liveness and readiness probes"},
        {"name": "valuation", "description": "DCF, WACC, and macro data for Latam SMEs"},
    ],
)

# CORS: explicit list (no wildcard with credentials)
cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(valuation_router)
app.include_router(embi_router)
