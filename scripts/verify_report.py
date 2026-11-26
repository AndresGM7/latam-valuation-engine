"""End-to-end verification script (mirrors the verification steps in the task)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PyPDF2 import PdfReader

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

print("=" * 70)
print("VERIFICATION 1: pytest tests/unit/test_pdf_generator.py")
print("=" * 70)
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/unit/test_pdf_generator.py", "-v"],
    capture_output=True, text=True,
)
print(r.stdout[-2000:])
print("RETURN CODE:", r.returncode)
assert r.returncode == 0, "Unit tests failed"

print()
print("=" * 70)
print("VERIFICATION 2: python examples/generate_report.py")
print("=" * 70)
r = subprocess.run(
    [sys.executable, "examples/generate_report.py"],
    capture_output=True, text=True,
)
print(r.stdout)
print("STDERR:", r.stderr[-500:] if r.stderr else "(none)")
print("RETURN CODE:", r.returncode)
assert r.returncode == 0, "Generate report failed"

print()
print("=" * 70)
print("VERIFICATION 3: PDF exists at reports/latam_valuation_report_v0.2.pdf")
print("=" * 70)
pdf_path = ROOT / "reports" / "latam_valuation_report_v0.2.pdf"
exists = os.path.exists(str(pdf_path))
size_kb = pdf_path.stat().st_size / 1024 if exists else 0
print(f"Path: {pdf_path}")
print(f"Exists: {exists}")
print(f"Size: {size_kb:.1f} KB")
assert exists

print()
print("=" * 70)
print("VERIFICATION 4: PDF has at least 5 pages")
print("=" * 70)
reader = PdfReader(str(pdf_path))
n_pages = len(reader.pages)
print(f"Pages: {n_pages}")
assert n_pages >= 5

print()
print("=" * 70)
print("VERIFICATION 5: Read back paragraphs to confirm content")
print("=" * 70)
all_text = "\n".join(p.extract_text() or "" for p in reader.pages)
checks = [
    "latam-valuation-engine",
    "Validating Latam DCF against Sell-Side",
    "Ecopetrol",
    "YPF",
    "Path A",
    "Path B",
    "two-stage",
    "Damodaran",
    "Bancolombia",
    "39,371",  # Ecopetrol year-1 revenue formatted
    "18,000",  # YPF year-1 revenue formatted
]
for kw in checks:
    found = kw in all_text
    mark = "OK" if found else "FAIL"
    print(f"  [{mark}] contains '{kw}'")
    assert found, f"Missing required text: {kw}"

print()
print("=" * 70)
print("VERIFICATION 6: Full test suite — no regressions")
print("=" * 70)
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q"],
    capture_output=True, text=True,
)
print(r.stdout[-1500:])
print("RETURN CODE:", r.returncode)
assert r.returncode == 0, "Regression in test suite"

print()
print("=" * 70)
print("ALL VERIFICATIONS PASSED")
print("=" * 70)
print(f"PDF: {pdf_path}")
print(f"Pages: {n_pages}")
print(f"Size: {size_kb:.1f} KB")
