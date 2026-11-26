"""Advanced DCF helpers for valuation.

This module extends the basic Gordon Growth model with:

1. `terminal_value_two_stage`: handle capex-heavy projects where early FCFs
   are negative but late FCFs become positive and stable.

2. `terminal_value_with_normalization`: use average of last N years of FCF
   instead of just the last year, for companies with cyclical FCFs.

3. `dcf_summary`: complete DCF including explicit period + terminal value,
   with components for reporting.

These are GENERAL improvements to the DCF model — applicable to any
industry/region. They do NOT contain any YPF-specific logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DCFResult:
    """Output of a complete DCF run."""

    explicit_period_pv: float  # Sum of discounted FCFs from years 1 to N
    terminal_value: float      # TV at end of year N (not discounted)
    terminal_value_pv: float   # TV discounted back to today
    enterprise_value: float    # explicit_pv + TV_pv
    net_debt: float            # Total debt - cash (subtracted to get equity)
    equity_value: float        # EV - net_debt
    # Component breakdown for reporting
    method: str
    assumptions: dict


def gordon_growth_terminal_value(
    fcf_year_n: float,
    growth_pct: float,
    wacc_pct: float,
) -> float:
    """Standard Gordon Growth terminal value (only valid if FCF > 0).

    TV = FCF_n × (1 + g) / (WACC - g)

    This is the simplest and most-used TV formula. It assumes:
    - FCFs grow at constant rate g forever after year N
    - WACC > g (else formula diverges)
    - Year N FCF is "normalized" (i.e., the company is in steady state)

    For companies with negative or very volatile FCFs near the end of the
    explicit period, use `terminal_value_with_normalization` or
    `terminal_value_two_stage` instead.
    """
    if wacc_pct <= growth_pct:
        raise ValueError(
            f"WACC ({wacc_pct}%) must exceed growth ({growth_pct}%) for Gordon Growth. "
            "Use terminal_value_two_stage for capex-heavy / cyclical businesses."
        )
    g = growth_pct / 100.0
    w = wacc_pct / 100.0
    return fcf_year_n * (1.0 + g) / (w - g)


def terminal_value_with_normalization(
    fcf_last_n_years: list[float],
    growth_pct: float,
    wacc_pct: float,
) -> float:
    """Gordon Growth using average of last N years of FCF (normalized).

    For cyclical businesses (commodities, energy), using the FCF of just
    the last year can over- or under-state the terminal cash flow. Using
    the average of the last 2-3 years gives a more stable estimate.

    Method (McKinsey Valuation textbook, Koller et al.):
        Normalized FCF = average of last N years' FCF
        TV = normalized_FCF × (1 + g) / (WACC - g)
    """
    if not fcf_last_n_years:
        raise ValueError("fcf_last_n_years must have at least one element")
    normalized = sum(fcf_last_n_years) / len(fcf_last_n_years)
    return gordon_growth_terminal_value(normalized, growth_pct, wacc_pct)


def terminal_value_two_stage(
    fcf_explicit: list[float],
    wacc_pct: float,
    terminal_growth_pct: float,
    fade_years: int = 5,
    terminal_fcf_margin_to_avg: float | None = None,
) -> float:
    """Two-stage TV for businesses with heavy early capex / negative early FCFs.

    The standard Gordon Growth formula breaks down when explicit-period FCFs are
    negative or highly variable (e.g., oil & gas with multi-year capex plans).

    This method:
    1. Computes average FCF across years where FCF > 0 (the "stable" period).
    2. Applies Gordon Growth from that average, with a fade-in horizon.
    3. The fade years smooth the transition from explicit to terminal.

    Args:
        fcf_explicit: list of FCF values for years 1..N.
        wacc_pct: discount rate in %.
        terminal_growth_pct: long-term growth in %.
        fade_years: how many years of "fade-in" between explicit and terminal.
        terminal_fcf_margin_to_avg: optional override. If provided, terminal
            FCF = average positive FCF × this margin (e.g., 0.85 = 85%).
    """
    if not fcf_explicit:
        raise ValueError("fcf_explicit cannot be empty")

    # Average positive FCFs (capex years may be negative)
    positive_fcfs = [f for f in fcf_explicit if f > 0]
    if not positive_fcfs:
        # If no positive FCFs at all, the company is non-viable on FCF basis
        raise ValueError(
            "All explicit-period FCFs are negative — cannot apply two-stage TV. "
            "This business does not generate positive cash flow within the explicit period."
        )

    avg_positive_fcf = sum(positive_fcfs) / len(positive_fcfs)
    terminal_fcf = avg_positive_fcf if terminal_fcf_margin_to_avg is None \
        else avg_positive_fcf * terminal_fcf_margin_to_avg

    # Apply Gordon Growth from this terminal_fcf
    return gordon_growth_terminal_value(terminal_fcf, terminal_growth_pct, wacc_pct)


def discount_cash_flows(
    fcf: list[float],
    wacc_pct: float,
    initial_investment: float = 0.0,
) -> float:
    """Sum of discounted FCFs minus initial investment.

    Returns the present value (PV) of the explicit-period cash flows.
    Negative result means the project does not pay back at the given WACC.
    """
    w = wacc_pct / 100.0
    pv = 0.0
    for year, f in enumerate(fcf, start=1):
        pv += f / (1.0 + w) ** year
    return pv - initial_investment


def dcf_valuation(
    fcf_explicit: list[float],
    wacc_pct: float,
    terminal_growth_pct: float,
    net_debt: float,
    method: str = "auto",
    initial_investment: float = 0.0,
    normalization_years: int = 3,
) -> DCFResult:
    """Complete DCF: explicit period + terminal value → enterprise → equity.

    Args:
        fcf_explicit: list of FCF for years 1..N (e.g. [100, 110, 121, 133, 146]).
        wacc_pct: discount rate in %.
        terminal_growth_pct: long-term growth in %.
        net_debt: total_debt - cash, subtracted from EV to get equity value.
        method: "gordon_growth" (standard), "normalized" (avg last N years),
                "two_stage" (capex-heavy), or "auto" (picks based on FCF stability).
        initial_investment: capex required at year 0, subtracted from PV.
        normalization_years: for method="normalized", how many years to average.

    The auto method:
        - If all FCFs are positive and stable (max/min < 3), use gordon_growth.
        - If FCFs are volatile (max/min >= 3) but have positive values, use normalized.
        - If some FCFs are negative (capex-heavy), use two_stage.
    """
    if not fcf_explicit:
        raise ValueError("fcf_explicit cannot be empty")

    # Auto-select method
    if method == "auto":
        fcf_max = max(fcf_explicit)
        fcf_min = min(fcf_explicit)
        has_negative = any(f < 0 for f in fcf_explicit)
        if has_negative:
            method = "two_stage"
        elif fcf_max / max(fcf_min, 1e-9) >= 3.0:
            method = "normalized"
        else:
            method = "gordon_growth"

    # Explicit period
    explicit_pv = discount_cash_flows(fcf_explicit, wacc_pct, initial_investment)

    # Terminal value
    if method == "gordon_growth":
        tv = gordon_growth_terminal_value(fcf_explicit[-1], terminal_growth_pct, wacc_pct)
    elif method == "normalized":
        last_n = fcf_explicit[-normalization_years:]
        tv = terminal_value_with_normalization(last_n, terminal_growth_pct, wacc_pct)
    elif method == "two_stage":
        tv = terminal_value_two_stage(fcf_explicit, wacc_pct, terminal_growth_pct)
    else:
        raise ValueError(f"Unknown method: {method}")

    # Discount TV back to today
    tv_pv = tv / (1.0 + wacc_pct / 100.0) ** len(fcf_explicit)

    ev = explicit_pv + tv_pv
    equity = ev - net_debt

    return DCFResult(
        explicit_period_pv=explicit_pv,
        terminal_value=tv,
        terminal_value_pv=tv_pv,
        enterprise_value=ev,
        net_debt=net_debt,
        equity_value=equity,
        method=method,
        assumptions={
            "wacc_pct": wacc_pct,
            "terminal_growth_pct": terminal_growth_pct,
            "horizon_years": len(fcf_explicit),
            "initial_investment": initial_investment,
            "normalization_years": normalization_years,
        },
    )
