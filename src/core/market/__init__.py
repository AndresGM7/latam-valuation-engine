"""Market sizing, population, and CANVAS segment data."""
from .demographics import (
    CountryCode, CountryDemographics, CityDemographics, MarketSizing,
    compute_market_size, get_country, get_city, list_cities,
    COUNTRIES_2025, CITIES_2024,
)

__all__ = [
    "CountryCode", "CountryDemographics", "CityDemographics", "MarketSizing",
    "compute_market_size", "get_country", "get_city", "list_cities",
    "COUNTRIES_2025", "CITIES_2024",
]
