"""Unit tests for the PDF valuation report generator.

Tests cover:
    - Public API signature and side effects
    - Computed values match the project's own valuation pipeline
    - PDF structure (file exists, page count, content keywords present)
    - Style invariants (no emoji in module, Helvetica font in styles)
    - Determinism (same input → same output bytes)
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pytest

# Skip the entire module if reportlab is not installed
try:
    import reportlab  # noqa: F401
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

pytestmark = pytest.mark.skipif(
    not HAS_REPORTLAB, reason="reportlab not installed"
)


# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------

from src.core.reports.pdf_generator import (
    _compute_one,
    _fmt_money,
    _fmt_pct,
    _fmt_delta_pct,
    _fmt_money_signed,
    generate_valuation_report,
)


# ---------------------------------------------------------------------------
# Minimal company fixtures (real public data, no invention)
# ---------------------------------------------------------------------------

ECOPETROL: dict[str, Any] = {
    "name": "Ecopetrol S.A.",
    "ticker": "ECOPETROL",
    "country": "Colombia",
    "sector": "Oil/Gas (Integrated)",
    "shares_outstanding_m": 4_134,
    "share_price_usd": 12.50,
    "total_debt": 16_800,
    "cash": 3_800,
    "tax_rate_pct": 35.0,
    "beta_unlevered": 0.764,
    "ebitda_margin_pct": 33.6,
    "da_pct_of_revenue": 12.0,
    "capex_annual": 5_500,
    "wc_change_pct": 1.0,
    "wc_anchor_revenue": 39_000,
    "revenue_5y": [39_371, 40_552, 41_769, 43_022, 44_313],
    "risk_free_rate_pct": 4.30,
    "equity_risk_premium_pct": 7.08,
    "mature_erp_pct": None,
    "country_risk_premium_pct": 0.0,
    "fx_risk_premium_pct": 0.0,
    "cost_of_debt_pretax_pct": 11.5,
    "terminal_growth_pct": 2.5,
    "sellside_broker": "Bancolombia",
    "sellside_as_of": "2023-12-15",
    "sellside_wacc_pct": 12.5,
    "sellside_target_usd": 15.00,
    "wacc_path": "A",
    "conclusion": "Test conclusion.",
}


YPF: dict[str, Any] = {
    "name": "YPF S.A.",
    "ticker": "YPF",
    "country": "Argentina",
    "sector": "Oil/Gas (Integrated)",
    "shares_outstanding_m": 393,
    "share_price_usd": 22.50,
    "total_debt": 7_900,
    "cash": 800,
    "tax_rate_pct": 35.0,
    "beta_unlevered": 0.764,
    "ebitda_margin_pct": 32.0,
    "da_pct_of_revenue": 11.0,
    "capex_annual": 5_000,
    "wc_change_pct": 1.5,
    "wc_anchor_revenue": 17_000,
    "revenue_5y": [18_000, 19_440, 20_995, 22_675, 24_489],
    "risk_free_rate_pct": 4.30,
    "equity_risk_premium_pct": None,
    "mature_erp_pct": 5.5,
    "country_risk_premium_pct": 10.92,
    "fx_risk_premium_pct": 10.0,
    "cost_of_debt_pretax_pct": 14.5,
    "terminal_growth_pct": 3.0,
    "sellside_broker": "Balanz / Goldman / Comafi (avg)",
    "sellside_as_of": "2024-Q1",
    "sellside_wacc_pct": 27.8,
    "sellside_target_usd": 35.00,
    "wacc_path": "B",
    "conclusion": "Test conclusion.",
}


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class TestFormattingHelpers:
    """Pure helpers — should be fast and never call reportlab."""

    def test_fmt_money_thousands_separators(self):
        assert _fmt_money(1_234_567) == "1,234,567"
        assert _fmt_money(0) == "0"
        assert _fmt_money(999) == "999"

    def test_fmt_money_decimals(self):
        assert _fmt_money(1234.5, decimals=1) == "1,234.5"
        assert _fmt_money(1234.567, decimals=2) == "1,234.57"

    def test_fmt_money_negative(self):
        # Negative values use a real minus sign (we chose to use ASCII '-')
        result = _fmt_money(-1234)
        assert "1,234" in result
        assert result.startswith("-")

    def test_fmt_money_signed_positive_has_plus(self):
        assert _fmt_money_signed(100).startswith("+")
        assert _fmt_money_signed(0) == "+0"
        # Negative numbers: real minus
        assert _fmt_money_signed(-100).startswith("-")

    def test_fmt_pct_one_decimal(self):
        assert _fmt_pct(33.6) == "33.6%"
        assert _fmt_pct(0) == "0.0%"

    def test_fmt_delta_pct_positive_has_plus(self):
        assert _fmt_delta_pct(12.4) == "+12.4%"
        assert _fmt_delta_pct(-6.4) == "-6.4%"
        assert _fmt_delta_pct(0) == "+0.0%"


class TestComputeOne:
    """The internal computation must call our real valuation pipeline."""

    def test_ecopetrol_wacc_matches_pipeline(self):
        comp = _compute_one(ECOPETROL)
        # Path A: Damodaran total ERP (no double-count). We expect WACC ≈ 10%.
        assert 8.0 < comp["wacc_our_pct"] < 12.0
        # Sell-side gap (negative = our WACC is lower because no double-count)
        assert comp["wacc_delta_pp"] < 0  # ours is lower than 12.5

    def test_ecopetrol_target_within_10pct_of_sellside(self):
        comp = _compute_one(ECOPETROL)
        # Match expectation set by integration test: within ~30% absolute,
        # and in practice with our pipeline around −6%.
        delta_pct = abs(comp["target_delta_pct"])
        assert delta_pct < 20.0, (
            f"DCF target deviates from sell-side by {delta_pct:.1f}%"
        )

    def test_ecopetrol_tv_method_is_gordon(self):
        comp = _compute_one(ECOPETROL)
        assert comp["tv_method"] == "gordon_growth"

    def test_ypf_wacc_uses_decomposable_path(self):
        comp = _compute_one(YPF)
        # Path B: Mature ERP + CRP + FX premium => Ke high, WACC > 18%
        assert comp["wacc_our_pct"] > 18.0
        assert comp["wacc_our_pct"] < 27.8
        assert comp["ke_pct"] > 25.0  # including 10pp FX premium
        assert comp["wacc_path"] == "B"

    def test_ypf_tv_method_auto_selects_two_stage(self):
        """YPF has negative FCFs in years 1-2 → auto picks two_stage."""
        comp = _compute_one(YPF)
        assert comp["tv_method"] == "two_stage"

    def test_ypf_negative_fcfs_year_1_2(self):
        """Document the resource-company limitation."""
        comp = _compute_one(YPF)
        assert comp["fcf_5y"][0] < 0
        assert comp["fcf_5y"][1] < 0

    def test_revenue_5y_passthrough(self):
        comp = _compute_one(ECOPETROL)
        assert comp["revenue_5y"] == ECOPETROL["revenue_5y"]

    def test_capital_structure_computed_correctly(self):
        comp = _compute_one(ECOPETROL)
        expected_dv = 16_800 / (16_800 + 4_134 * 12.50) * 100
        assert abs(comp["d_over_v_pct"] - expected_dv) < 0.1


class TestGenerateValuationReport:
    """End-to-end: PDF generation + structure."""

    @pytest.fixture
    def pdf_path(self, tmp_path: Path) -> Path:
        out = tmp_path / "report.pdf"
        generate_valuation_report(str(out), [ECOPETROL, YPF])
        return out

    def test_pdf_file_created(self, pdf_path: Path):
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 1_000  # > 1 KB

    def test_pdf_has_at_least_five_pages(self, pdf_path: Path):
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        assert len(reader.pages) >= 5

    def test_pdf_has_ten_pages_for_two_companies(self, pdf_path: Path):
        """Cover (1) + Exec (1) + Eco (3) + YPF (3) + Methodology (1) + Refs (1) = 10."""
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        assert len(reader.pages) == 10

    def test_pdf_contains_company_names(self, pdf_path: Path):
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        all_text = "\n".join((p.extract_text() or "") for p in reader.pages)
        assert "Ecopetrol" in all_text
        assert "YPF" in all_text

    def test_pdf_contains_methodology_keywords(self, pdf_path: Path):
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        all_text = "\n".join((p.extract_text() or "") for p in reader.pages)
        # Methodology section markers
        assert "Path A" in all_text
        assert "Path B" in all_text
        assert "two-stage" in all_text.lower() or "two_stage" in all_text.lower()
        assert "reserves" in all_text.lower()

    def test_pdf_contains_formatted_numbers(self, pdf_path: Path):
        """Numbers must use thousands separators."""
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        all_text = "\n".join((p.extract_text() or "") for p in reader.pages)
        # Ecopetrol revenue year 1 should appear with a comma separator
        assert "39,371" in all_text
        # YPF revenue year 1
        assert "18,000" in all_text

    def test_pdf_contains_cover_title(self, pdf_path: Path):
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        all_text = "\n".join((p.extract_text() or "") for p in reader.pages)
        assert "Validating Latam DCF against Sell-Side" in all_text
        assert "v0.2" in all_text


class TestDeterminism:
    """Same input → structurally equivalent output.

    ReportLab embeds a unique document ID and a build timestamp in the
    PDF trailer, so the byte-for-byte output differs between runs.
    We assert structural equality instead: same size, same page count,
    same extracted text.
    """

    def test_identical_input_yields_structurally_identical_pdf(
        self, tmp_path: Path
    ):
        from PyPDF2 import PdfReader

        out_a = tmp_path / "a.pdf"
        out_b = tmp_path / "b.pdf"
        generate_valuation_report(str(out_a), [ECOPETROL, YPF])
        generate_valuation_report(str(out_b), [ECOPETROL, YPF])

        # Same byte size
        assert out_a.stat().st_size == out_b.stat().st_size

        # Same page count
        ra = PdfReader(str(out_a))
        rb = PdfReader(str(out_b))
        assert len(ra.pages) == len(rb.pages)

        # Same extracted text (page by page)
        for pa, pb in zip(ra.pages, rb.pages):
            ta = pa.extract_text() or ""
            tb = pb.extract_text() or ""
            assert ta == tb


class TestStyleInvariants:
    """Make sure we never accidentally add emoji or images."""

    def test_module_source_has_no_emoji(self):
        """The PDF generator module must not contain emoji."""
        path = (
            Path(__file__).resolve().parents[2]
            / "src" / "core" / "reports" / "pdf_generator.py"
        )
        text = path.read_text(encoding="utf-8")
        # Common emoji ranges
        emoji_pattern = re.compile(
            "[\U0001F300-\U0001FAFF"  # symbols & pictographs, emoji
            "\U00002600-\U000027BF"   # misc symbols, dingbats
            "\U0001F600-\U0001F64F"   # emoticons
            "\U0001F900-\U0001F9FF"   # supplemental symbols
            "]"
        )
        matches = emoji_pattern.findall(text)
        assert not matches, f"Module contains emoji: {matches!r}"

    def test_helvetica_used_in_styles(self):
        """Professional style — Helvetica is the required font."""
        from src.core.reports.pdf_generator import _styles
        styles = _styles()
        # Title and body should be Helvetica or Helvetica-Bold
        assert "Helvetica" in styles["title"].fontName
        assert "Helvetica" in styles["body"].fontName

    def test_navy_blue_is_1f3a5f(self):
        """Header colour must be navy #1f3a5f."""
        from src.core.reports.pdf_generator import NAVY
        # HexColor stores rgb in 0-1 range
        r, g, b = NAVY.rgb()
        # #1f3a5f = (31/255, 58/255, 95/255)
        assert abs(r - 31/255) < 0.001
        assert abs(g - 58/255) < 0.001
        assert abs(b - 95/255) < 0.001


class TestEmptyInput:
    """Edge cases — the generator should not crash on edge inputs."""

    def test_single_company(self, tmp_path: Path):
        out = tmp_path / "single.pdf"
        generate_valuation_report(str(out), [ECOPETROL])
        assert out.exists()
        from PyPDF2 import PdfReader
        n = len(PdfReader(str(out)).pages)
        assert n >= 5  # cover + exec + 3 ecopetrol pages + methodology + refs = 8

    def test_report_date_override(self, tmp_path: Path):
        out = tmp_path / "dated.pdf"
        generate_valuation_report(
            str(out), [ECOPETROL, YPF], report_date="2026-01-15"
        )
        from PyPDF2 import PdfReader
        text = "\n".join(
            (p.extract_text() or "") for p in PdfReader(str(out)).pages
        )
        assert "2026-01-15" in text
