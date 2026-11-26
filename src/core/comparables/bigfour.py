"""Comparables module: parse and compare against published Big 4 / sell-side valuations.

Use cases:
1. Validate the latam-valuation-engine output against a published DCF
2. Reverse-engineer the WACC / growth assumptions a sell-side analyst used
3. Show users "here's what McKinsey/PwC/etc. said; here's what we say"

Sources we support:
- Public equity research reports (PDFs)
- Investor presentations
- Annual reports (10-K equivalent for Latam)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class BigFourValuation:
    """A published valuation from a Big 4 / sell-side analyst.

    Fields are kept minimal but auditable. The point is to compare
    our engine's output against a real external number.
    """

    company: str
    ticker: str
    country: str  # ISO
    as_of: date
    source_firm: str  # "McKinsey", "PwC", "Goldman Sachs", etc.
    document_url: Optional[str] = None
    document_path: Optional[Path] = None

    # Core valuation numbers (in USD millions unless noted)
    enterprise_value_usd_m: float = 0.0
    equity_value_usd_m: float = 0.0
    wacc_pct: float = 0.0
    terminal_growth_pct: float = 0.0
    forecast_horizon_years: int = 5

    # Methodology (extracted from the report)
    explicit_cash_flows_usd_m: list[float] = None  # type: ignore
    country_risk_premium_pct: float = 0.0
    beta_levered: float = 0.0
    beta_unlevered: float = 0.0
    cost_of_equity_pct: float = 0.0
    cost_of_debt_pretax_pct: float = 0.0
    tax_rate_pct: float = 0.0
    debt_to_equity: float = 0.0

    notes: str = ""

    def __post_init__(self):
        if self.explicit_cash_flows_usd_m is None:
            object.__setattr__(self, "explicit_cash_flows_usd_m", [])


def parse_mckinsey_dcf(pdf_path: Path) -> BigFourValuation:
    """Extract DCF components from a McKinsey-style report.

    McKinsey's "Valuation" textbook (Koller, Goedhart, Wessels) uses a
    5-10 year DCF with explicit FCF + terminal value. Their reports
    typically state WACC, beta, growth, and FCF in standard tables.

    This parser is heuristic and best-effort. Always verify against the source.
    """
    import pdfplumber  # type: ignore

    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            full_text += t + "\n"

    # Extract heuristics
    def find_float(pattern: str, default: float = 0.0) -> float:
        m = re.search(pattern, full_text, re.IGNORECASE)
        if not m:
            return default
        try:
            return float(m.group(1).replace(",", ""))
        except (ValueError, IndexError):
            return default

    # Look for the firm name in the document
    firm = "Unknown"
    for candidate in ("McKinsey", "PwC", "Deloitte", "EY", "KPMG", "Goldman", "Morgan Stanley", "JP Morgan"):
        if candidate.lower() in full_text.lower():
            firm = candidate
            break

    return BigFourValuation(
        company="Unknown",  # caller fills in
        ticker="Unknown",
        country="Unknown",
        as_of=date.today(),
        source_firm=firm,
        document_path=pdf_path,
        wacc_pct=find_float(r"WACC[:\s]+(\d+\.?\d*)\s*%"),
        cost_of_equity_pct=find_float(r"cost of equity[:\s]+(\d+\.?\d*)\s*%"),
        cost_of_debt_pretax_pct=find_float(r"cost of debt[:\s]+(\d+\.?\d*)\s*%"),
        beta_levered=find_float(r"levered beta[:\s]+(\d+\.?\d*)"),
        beta_unlevered=find_float(r"unlevered beta[:\s]+(\d+\.?\d*)"),
        country_risk_premium_pct=find_float(r"country risk premium[:\s]+(\d+\.?\d*)\s*%"),
        terminal_growth_pct=find_float(r"terminal growth[:\s]+(\d+\.?\d*)\s*%"),
        tax_rate_pct=find_float(r"tax rate[:\s]+(\d+\.?\d*)\s*%"),
    )


def compare_valuations(
    our_dcf: dict,
    published: BigFourValuation,
) -> dict:
    """Compare our DCF result against a published Big 4 / sell-side valuation.

    Returns a structured comparison dict suitable for a UI table.
    """
    our_vpn = sum(our_dcf.get("free_cash_flow", [])) - our_dcf.get("inversion_inicial", 0)
    # We don't have EV directly without running DCF; this would integrate with the full engine
    return {
        "our_metrics": {
            "wacc_pct": our_dcf.get("wacc_pct"),
            "vpn_usd_m": our_vpn,
            "country": our_dcf.get("country"),
            "industry": our_dcf.get("industry"),
            "horizon_years": our_dcf.get("horizon_years"),
        },
        "published_metrics": {
            "source_firm": published.source_firm,
            "as_of": published.as_of,
            "enterprise_value_usd_m": published.enterprise_value_usd_m,
            "wacc_pct": published.wacc_pct,
            "cost_of_equity_pct": published.cost_of_equity_pct,
            "country_risk_premium_pct": published.country_risk_premium_pct,
            "beta_levered": published.beta_levered,
            "terminal_growth_pct": published.terminal_growth_pct,
        },
        "deltas": {
            "wacc_delta_pct": (our_dcf.get("wacc_pct") or 0) - published.wacc_pct,
        },
        "notes": [
            "Comparison assumes same revenue projections, depreciation, and tax treatment.",
            "Differences typically arise from WACC components (CRP, beta, leverage).",
            "Always sanity-check by triangulating with multiples-based valuation.",
        ],
    }
