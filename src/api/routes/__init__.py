"""Routes package."""

from .valuation import router as valuation_router
from .health import router as health_router
from .embi import router as embi_router

__all__ = ["valuation_router", "health_router", "embi_router"]
