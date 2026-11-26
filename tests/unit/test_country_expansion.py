
"""Test that all Latam countries produce monotonically reasonable WACC rankings."""

from src.core.valuation import wacc_from_defaults, Country


def test_all_latam_countries_have_defaults():
    """All Latam countries should have WACC defaults configured."""
    countries = [Country.MEXICO, Country.CHILE, Country.BRAZIL, Country.PERU,
                 Country.COLOMBIA, Country.ARGENTINA, Country.UNITED_STATES]
    for c in countries:
        r = wacc_from_defaults(c, beta_unlevered=1.0, debt_to_total_capital_pct=30.0)
        assert 5.0 < r.wacc_pct < 35.0, f"{c.value} WACC {r.wacc_pct:.2f}% outside reasonable range"


def test_country_risk_ordering():
    """Lower credit rating => higher WACC."""
    us = wacc_from_defaults(Country.UNITED_STATES, 1.0, 30.0)
    cl = wacc_from_defaults(Country.CHILE, 1.0, 30.0)        # A
    mx = wacc_from_defaults(Country.MEXICO, 1.0, 30.0)       # Baa2
    co = wacc_from_defaults(Country.COLOMBIA, 1.0, 30.0)     # Baa3
    br = wacc_from_defaults(Country.BRAZIL, 1.0, 30.0)       # Ba2
    ar = wacc_from_defaults(Country.ARGENTINA, 1.0, 30.0)    # Caa1
    # Ordering should follow sovereign ratings
    assert us.wacc_pct < cl.wacc_pct, f"US {us.wacc_pct:.2f}% should be < CL {cl.wacc_pct:.2f}%"
    assert cl.wacc_pct < mx.wacc_pct, f"CL {cl.wacc_pct:.2f}% should be < MX {mx.wacc_pct:.2f}%"
    assert mx.wacc_pct < co.wacc_pct, f"MX {mx.wacc_pct:.2f}% should be < CO {co.wacc_pct:.2f}%"
    assert co.wacc_pct < br.wacc_pct, f"CO {co.wacc_pct:.2f}% should be < BR {br.wacc_pct:.2f}%"
    assert br.wacc_pct < ar.wacc_pct, f"BR {br.wacc_pct:.2f}% should be < AR {ar.wacc_pct:.2f}%"


def test_argentina_wacc_dominates_latam():
    """Argentina's WACC should be at least 2x the lowest Latam WACC (huge country risk)."""
    ar = wacc_from_defaults(Country.ARGENTINA, 1.0, 30.0)
    cl = wacc_from_defaults(Country.CHILE, 1.0, 30.0)  # lowest Latam
    assert ar.wacc_pct > 2.0 * cl.wacc_pct,         f"AR {ar.wacc_pct:.2f}% should be > 2x CL {cl.wacc_pct:.2f}%"
