"""Tests for the EMBI Latam historical dataset loader."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from src.core.macro.embi import EMBIDataset, load_embi


class TestEMBIDataset:
    def test_load_singleton(self):
        ds = load_embi()
        assert isinstance(ds, EMBIDataset)

    def test_countries_listed(self):
        ds = load_embi()
        countries = ds.countries
        # Spot-check critical Latam markets
        for c in ["Argentina", "Colombia", "Brasil", "México", "Chile", "Perú"]:
            assert c in countries, f"Missing country: {c}"

    def test_latest_date_is_recent(self):
        ds = load_embi()
        today = date.today()
        delta = (today - ds.latest_date).days
        # Dataset is updated weekly-ish; within 14 days is fine
        assert delta <= 14, f"Dataset is stale: {delta} days old"

    def test_argentina_latest_in_extreme_range(self):
        ds = load_embi()
        r = ds.latest("Argentina")
        assert r is not None
        # Argentina EMBI is structurally > 5% even in good times
        assert 5.0 < r.spread_pct < 25.0, f"AR EMBI out of expected range: {r.spread_pct}"

    def test_chile_latest_in_low_range(self):
        ds = load_embi()
        r = ds.latest("Chile")
        assert r is not None
        # Chile is investment grade, EMBI < 3% expected
        assert r.spread_pct < 3.0, f"CL EMBI unexpectedly high: {r.spread_pct}"

    def test_30d_moving_average(self):
        ds = load_embi()
        r = ds.moving_average("Colombia", window_days=30)
        assert r is not None
        assert r.is_30d_avg
        assert r.std_30d_pct >= 0

    def test_historical_returns_pandas_series(self):
        ds = load_embi()
        end = date.today()
        start = end - timedelta(days=90)
        s = ds.historical("Brasil", start=start, end=end)
        assert len(s) > 0
        assert s.name == "Brasil"

    def test_unknown_country_returns_none(self):
        ds = load_embi()
        assert ds.latest("Atlantis") is None
        assert ds.moving_average("Atlantis") is None

    def test_embi_for_country_convenience(self):
        from src.core.macro.embi import embi_for_country
        r = embi_for_country("Argentina", window_days=30)
        assert r is not None
        assert r.is_30d_avg
