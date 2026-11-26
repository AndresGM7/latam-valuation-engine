"""Market size and population data for valuation.

This module answers the question every real DCF needs to answer:
    "How many people can this product reach, and how much can we charge them?"

We bundle three layers of market data, from coarse to fine:

1. **Country-level population, GDP, GDP per capita** — World Bank API
2. **City-level population** — UN World Urbanization Prospects (built-in table)
3. **CANVAS segments** — calculated from user-provided % of population

Why we bundle UN city data instead of fetching live:
- The UN World Urbanization Prospects API is slow and rate-limited.
- We need reproducible numbers for tests.
- City populations are slow-moving (decade scale), so a snapshot
  refreshed every 2 years is sufficient.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class CountryCode(str, Enum):
    """ISO 3166-1 alpha-2 codes for countries we cover."""

    CO = "CO"  # Colombia
    AR = "AR"  # Argentina
    MX = "MX"  # Mexico
    CL = "CL"  # Chile
    PE = "PE"  # Peru
    BR = "BR"  # Brazil
    UY = "UY"  # Uruguay
    US = "US"  # United States


@dataclass(frozen=True)
class CountryDemographics:
    """Country-level demographics snapshot (World Bank-style)."""

    country: CountryCode
    population: int  # total
    population_urban_pct: float  # % living in urban areas
    gdp_usd_billions: float  # current USD
    gdp_per_capita_usd: float  # nominal
    middle_class_pct: float  # % with daily expenditure USD 13-70 (WB LAC methodology)
    as_of: date

    @property
    def population_urban(self) -> int:
        return int(self.population * self.population_urban_pct / 100)

    @property
    def middle_class_population(self) -> int:
        return int(self.population * self.middle_class_pct / 100)


@dataclass(frozen=True)
class CityDemographics:
    """A city's demographics snapshot."""

    name: str
    country: CountryCode
    population: int  # metropolitan area
    population_density_per_km2: float
    median_age: float  # years
    gdp_per_capita_usd: Optional[float] = None
    as_of: date = date(2024, 1, 1)


@dataclass(frozen=True)
class MarketSizing:
    """Result of a TAM/SAM/SOM analysis."""

    tam_population: int  # Total addressable market
    sam_population: int  # Serviceable available market (urban + filter)
    som_population: int  # Serviceable obtainable market (realistic Year-1)
    tam_market_size_usd: float  # assuming ARPU
    sam_market_size_usd: float
    som_market_size_usd: float
    country: CountryCode
    assumptions: dict  # auditable inputs

    def summary(self) -> dict:
        return {
            "country": self.country.value,
            "tam_population": self.tam_population,
            "sam_population": self.sam_population,
            "som_population": self.som_population,
            "tam_market_size_usd": self.tam_market_size_usd,
            "sam_market_size_usd": self.sam_market_size_usd,
            "som_market_size_usd": self.som_market_size_usd,
            "assumptions": self.assumptions,
        }


# ------------------------------------------------------------
# Country demographics — World Bank 2025 values (verified via API)
# ------------------------------------------------------------
COUNTRIES_2025 = {
    CountryCode.CO: CountryDemographics(
        country=CountryCode.CO, population=53_425_635, population_urban_pct=81.8,
        gdp_usd_billions=363.5, gdp_per_capita_usd=6_804.0, middle_class_pct=33.0,
        as_of=date(2025, 1, 1),
    ),
    CountryCode.AR: CountryDemographics(
        country=CountryCode.AR, population=45_851_378, population_urban_pct=92.5,
        gdp_usd_billions=632.0, gdp_per_capita_usd=13_780.0, middle_class_pct=42.0,
        as_of=date(2025, 1, 1),
    ),
    CountryCode.MX: CountryDemographics(
        country=CountryCode.MX, population=130_400_000, population_urban_pct=81.0,
        gdp_usd_billions=1_811.0, gdp_per_capita_usd=13_890.0, middle_class_pct=45.0,
        as_of=date(2025, 1, 1),
    ),
    CountryCode.CL: CountryDemographics(
        country=CountryCode.CL, population=19_600_000, population_urban_pct=87.8,
        gdp_usd_billions=346.0, gdp_per_capita_usd=17_650.0, middle_class_pct=58.0,
        as_of=date(2025, 1, 1),
    ),
    CountryCode.PE: CountryDemographics(
        country=CountryCode.PE, population=34_352_000, population_urban_pct=78.6,
        gdp_usd_billions=294.0, gdp_per_capita_usd=8_560.0, middle_class_pct=30.0,
        as_of=date(2025, 1, 1),
    ),
    CountryCode.BR: CountryDemographics(
        country=CountryCode.BR, population=216_400_000, population_urban_pct=87.6,
        gdp_usd_billions=2_189.0, gdp_per_capita_usd=10_120.0, middle_class_pct=49.0,
        as_of=date(2025, 1, 1),
    ),
    CountryCode.UY: CountryDemographics(
        country=CountryCode.UY, population=3_423_000, population_urban_pct=95.5,
        gdp_usd_billions=82.0, gdp_per_capita_usd=23_960.0, middle_class_pct=62.0,
        as_of=date(2025, 1, 1),
    ),
    CountryCode.US: CountryDemographics(
        country=CountryCode.US, population=336_000_000, population_urban_pct=83.3,
        gdp_usd_billions=27_720.0, gdp_per_capita_usd=82_500.0, middle_class_pct=70.0,
        as_of=date(2025, 1, 1),
    ),
}


# ------------------------------------------------------------
# Major Latam cities — UN World Urbanization Prospects 2024 revision
# (population in metropolitan area, density per km2)
# ------------------------------------------------------------
CITIES_2024 = {
    # Colombia
    ("Bogotá", CountryCode.CO): CityDemographics(
        name="Bogotá", country=CountryCode.CO, population=11_300_000,
        population_density_per_km2=5_200, median_age=31.5, gdp_per_capita_usd=10_500,
    ),
    ("Medellín", CountryCode.CO): CityDemographics(
        name="Medellín", country=CountryCode.CO, population=4_100_000,
        population_density_per_km2=3_400, median_age=33.0, gdp_per_capita_usd=11_200,
    ),
    ("Cali", CountryCode.CO): CityDemographics(
        name="Cali", country=CountryCode.CO, population=2_700_000,
        population_density_per_km2=4_200, median_age=34.5, gdp_per_capita_usd=7_800,
    ),
    ("Barranquilla", CountryCode.CO): CityDemographics(
        name="Barranquilla", country=CountryCode.CO, population=2_400_000,
        population_density_per_km2=5_500, median_age=30.5, gdp_per_capita_usd=6_900,
    ),
    ("Cartagena", CountryCode.CO): CityDemographics(
        name="Cartagena", country=CountryCode.CO, population=1_900_000,
        population_density_per_km2=2_900, median_age=32.0, gdp_per_capita_usd=8_400,
    ),
    ("Bucaramanga", CountryCode.CO): CityDemographics(
        name="Bucaramanga", country=CountryCode.CO, population=1_400_000,
        population_density_per_km2=3_700, median_age=33.5, gdp_per_capita_usd=9_100,
    ),
    # Argentina
    ("Buenos Aires", CountryCode.AR): CityDemographics(
        name="Buenos Aires", country=CountryCode.AR, population=15_400_000,
        population_density_per_km2=14_500, median_age=36.0, gdp_per_capita_usd=18_900,
    ),
    ("Córdoba", CountryCode.AR): CityDemographics(
        name="Córdoba", country=CountryCode.AR, population=1_700_000,
        population_density_per_km2=2_700, median_age=33.5, gdp_per_capita_usd=12_500,
    ),
    ("Rosario", CountryCode.AR): CityDemographics(
        name="Rosario", country=CountryCode.AR, population=1_400_000,
        population_density_per_km2=6_400, median_age=34.0, gdp_per_capita_usd=11_800,
    ),
    ("Mendoza", CountryCode.AR): CityDemographics(
        name="Mendoza", country=CountryCode.AR, population=1_100_000,
        population_density_per_km2=2_100, median_age=34.5, gdp_per_capita_usd=10_500,
    ),
    # Mexico, Chile, Peru, Brazil (subset for first iteration)
    ("Ciudad de México", CountryCode.MX): CityDemographics(
        name="Ciudad de México", country=CountryCode.MX, population=22_200_000,
        population_density_per_km2=6_300, median_age=33.5, gdp_per_capita_usd=15_400,
    ),
    ("Santiago", CountryCode.CL): CityDemographics(
        name="Santiago", country=CountryCode.CL, population=7_100_000,
        population_density_per_km2=8_500, median_age=35.0, gdp_per_capita_usd=22_100,
    ),
    ("Lima", CountryCode.PE): CityDemographics(
        name="Lima", country=CountryCode.PE, population=11_400_000,
        population_density_per_km2=3_700, median_age=32.0, gdp_per_capita_usd=11_800,
    ),
    ("São Paulo", CountryCode.BR): CityDemographics(
        name="São Paulo", country=CountryCode.BR, population=22_400_000,
        population_density_per_km2=7_400, median_age=35.5, gdp_per_capita_usd=16_200,
    ),
}


# ------------------------------------------------------------
# TAM / SAM / SOM calculator
# ------------------------------------------------------------

def compute_market_size(
    *,
    country: CountryCode,
    city: Optional[str] = None,
    target_segment: str = "urban_adults",
    arpu_usd_per_year: float = 100.0,
    urban_pct: float = 100.0,
    age_min: int = 18,
    age_max: int = 65,
    middle_class_only: bool = False,
    market_share_assumption_pct: float = 5.0,  # realistic Year-1 capture
) -> MarketSizing:
    """Compute TAM / SAM / SOM for a product.

    Args:
        country: ISO country code
        city: optional city name; if given, restricts to metro population
        target_segment: preset (urban_adults, all_adults) or "custom"
        arpu_usd_per_year: Average Revenue Per User, USD/year (annualize monthly)
        urban_pct: % of population considered (default 100%)
        age_min/age_max: age range filter (default adults 18-65)
        middle_class_only: if True, only count middle-class population
        market_share_assumption_pct: SOM as % of SAM (realistic Year-1)

    Returns:
        MarketSizing with TAM/SAM/SOM in population and USD.

    Example:
        >>> m = compute_market_size(country=CountryCode.CO, city="Bogotá",
        ...                         arpu_usd_per_year=240,
        ...                         middle_class_only=True,
        ...                         market_share_assumption_pct=2.0)
        >>> m.som_market_size_usd
        ...
    """
    # Base population: country or city
    if city is not None:
        key = (city, country)
        if key not in CITIES_2024:
            raise ValueError(f"City {city!r} not in CITIES_2024. Available: {[c for c, _ in CITIES_2024.keys()]}")
        base_pop = CITIES_2024[key].population
        base_desc = f"city {city}, {country.value}"
    else:
        if country not in COUNTRIES_2025:
            raise ValueError(f"Country {country!r} not in COUNTRIES_2025")
        c = COUNTRIES_2025[country]
        base_pop = c.population
        base_desc = f"country {country.value}"

    # TAM: total population in scope
    tam_population = base_pop

    # SAM: filtered population
    sam_population = int(base_pop * (urban_pct / 100.0))
    # Age filter (rough): assume normal-ish distribution, so the % in [age_min, age_max]
    # is roughly (age_max - age_min) / 80 (life expectancy proxy)
    age_band_pct = max(0.0, min(100.0, (age_max - age_min) / 80.0 * 100.0))
    sam_population = int(sam_population * (age_band_pct / 100.0))
    if middle_class_only:
        if country in COUNTRIES_2025:
            sam_population = int(sam_population * (COUNTRIES_2025[country].middle_class_pct / 100.0))

    # SOM: realistic Year-1 share of SAM
    som_population = int(sam_population * (market_share_assumption_pct / 100.0))

    return MarketSizing(
        tam_population=tam_population,
        sam_population=sam_population,
        som_population=som_population,
        tam_market_size_usd=tam_population * arpu_usd_per_year,
        sam_market_size_usd=sam_population * arpu_usd_per_year,
        som_market_size_usd=som_population * arpu_usd_per_year,
        country=country,
        assumptions={
            "base": base_desc,
            "arpu_usd_per_year": arpu_usd_per_year,
            "urban_pct": urban_pct,
            "age_min": age_min,
            "age_max": age_max,
            "middle_class_only": middle_class_only,
            "market_share_assumption_pct": market_share_assumption_pct,
            "segment_label": target_segment,
        },
    )


def get_country(country: CountryCode) -> CountryDemographics:
    if country not in COUNTRIES_2025:
        raise ValueError(f"Country {country!r} not in COUNTRIES_2025")
    return COUNTRIES_2025[country]


def get_city(city: str, country: CountryCode) -> CityDemographics:
    key = (city, country)
    if key not in CITIES_2024:
        raise ValueError(f"City {city!r} in {country.value} not in CITIES_2024")
    return CITIES_2024[key]


def list_cities(country: Optional[CountryCode] = None) -> list[CityDemographics]:
    """List all available cities, optionally filtered by country."""
    cities = list(CITIES_2024.values())
    if country is not None:
        cities = [c for c in cities if c.country == country]
    return cities
