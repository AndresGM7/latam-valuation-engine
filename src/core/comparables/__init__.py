"""Comparables module: parse and compare against published Big 4 / sell-side valuations."""

from .bigfour import BigFourValuation, parse_mckinsey_dcf, compare_valuations

__all__ = ["BigFourValuation", "parse_mckinsey_dcf", "compare_valuations"]
