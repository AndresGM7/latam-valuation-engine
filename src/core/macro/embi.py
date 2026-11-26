"""EMBI Global Diversified historical series loader for Latam countries.

Source of truth:
    Banco Central de la República Dominicana (BCRD)
    https://www.bancentral.gov.do/a/d/2585-entorno-internacional

The file `data/macro/EMBI_Latam_BCRD.xlsx` contains daily EMBI spreads
(percent points, e.g. 2.61 = 261 bps) for 18 Latam countries plus
Global and LATINO aggregates, from 2007-10-29 to present.

Why we ship our own copy:
- The BCRD public URL has occasionally changed paths over the years.
- Having a local copy makes the engine fully reproducible offline.
- The data is public domain (BCRD publishes as public good).
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Data directory bundled with the package
_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "macro"
_DATASET_FILE = _DATA_DIR / "EMBI_Latam_BCRD.xlsx"


@dataclass(frozen=True)
class EMBIReading:
    """A single EMBI reading for a country."""

    country: str
    as_of: date
    spread_pct: float  # percent points (e.g. 2.61 = 261 bps)
    is_30d_avg: bool = False
    is_90d_avg: bool = False
    std_30d_pct: Optional[float] = None  # volatility in last 30 days


class EMBIDataset:
    """In-memory EMBI historical series with lookup helpers."""

    def __init__(self, xlsx_path: Path = _DATASET_FILE) -> None:
        if not xlsx_path.exists():
            raise FileNotFoundError(
                f"EMBI dataset not found at {xlsx_path}. "
                f"Download from https://www.bancentral.gov.do/a/d/2585-entorno-internacional "
                f"and save as {xlsx_path}"
            )
        # Header is on row 2 (row 1 has a title only)
        self.df = pd.read_excel(xlsx_path, sheet_name="Serie Histórica", header=1)
        # Normalize column names: strip whitespace, fix "REP DOM"
        self.df.columns = [str(c).strip() for c in self.df.columns]
        if "REP DOM" in self.df.columns:
            self.df = self.df.rename(columns={"REP DOM": "REP_DOM"})
        self.df["Fecha"] = pd.to_datetime(self.df["Fecha"], errors="coerce")
        self.df = self.df.dropna(subset=["Fecha"]).set_index("Fecha").sort_index()

    @property
    def countries(self) -> list[str]:
        """List of country columns (excluding 'Fecha', aggregates, and unnamed cols)."""
        return [
            c for c in self.df.columns
            if c not in ("Fecha", "Global", "LATINO", "RD-LATINO")
            and not c.startswith("Unnamed")
        ]

    @property
    def latest_date(self) -> date:
        return self.df.index[-1].date()

    def latest(self, country: str) -> Optional[EMBIReading]:
        """Most recent non-null reading for `country`."""
        if country not in self.df.columns:
            return None
        s = self.df[country].dropna()
        if s.empty:
            return None
        return EMBIReading(country=country, as_of=s.index[-1].date(), spread_pct=float(s.iloc[-1]))

    def moving_average(self, country: str, window_days: int = 30) -> Optional[EMBIReading]:
        """Last-N-business-days moving average and std."""
        if country not in self.df.columns:
            return None
        s = self.df[country].dropna().tail(window_days)
        if s.empty:
            return None
        avg = float(s.mean())
        std = float(s.std()) if len(s) > 1 else 0.0
        is_30d = window_days == 30
        is_90d = window_days == 90
        return EMBIReading(
            country=country,
            as_of=s.index[-1].date(),
            spread_pct=avg,
            is_30d_avg=is_30d,
            is_90d_avg=is_90d,
            std_30d_pct=std,
        )

    def historical(self, country: str, start: Optional[date] = None, end: Optional[date] = None) -> pd.Series:
        """Return the historical series for a country between dates (inclusive)."""
        if country not in self.df.columns:
            raise ValueError(f"Unknown country: {country}")
        s = self.df[country].dropna()
        if start:
            s = s[s.index.date >= start]
        if end:
            s = s[s.index.date <= end]
        return s


# Module-level singleton (lazy)
_singleton: Optional[EMBIDataset] = None


def load_embi() -> EMBIDataset:
    """Get the EMBI dataset (cached singleton)."""
    global _singleton
    if _singleton is None:
        _singleton = EMBIDataset()
    return _singleton


def embi_for_country(country_code: str, window_days: int = 30) -> Optional[EMBIReading]:
    """Convenience: get the latest N-day moving average for a country.

    Args:
        country_code: ISO 3166-1 alpha-3 or our internal code
            (ARG, BOL, BRA, CHL, COL, CRI, ECU, SLV, GTM, HND, MEX, PRY,
             PER, PAN, URY, VEN, DOM)
        window_days: 30 (default), 90, or any positive int.
    Returns:
        EMBIReading with moving average, or None if no data.
    """
    return load_embi().moving_average(country_code, window_days=window_days)
