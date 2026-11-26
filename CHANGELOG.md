# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-26 (in development)

### Added
- **Business Model Canvas + Value Proposition Design modules** (`src/core/canvas/`).
  Implements the Osterwalder 9-block BMC + VPD jobs/pains/gains + 3 types of fit.
  Credits: Osterwalder & Pigneur (2010), Osterwalder et al. (2014), Bland & Osterwalder
  (2019), and the user's own "Planeación Financiera bajo CANVAS" methodology
  (A. Giraldo & H. Ramos).
- **Bland & Osterwalder's 44 experiments library** — 17 experiments implemented
  with cost, duration, evidence_strength metadata.
- **EMBI Latam historical dataset** (`src/core/macro/embi.py`) — bundled from
  Banco Central de la República Dominicana. 18 countries, ~5,000 daily observations
  through 2026-11-24.
- **Market sizing module** (`src/core/market/`) — population data for 8 Latam
  countries + 14 major cities, TAM/SAM/SOM calculator.
- **Industry betas module** (`src/core/valuation/industry_betas.py`) — Damodaran
  Jan 2026 betas for 60 industries, indexed by sector.
- **WACC Path A/B decomposition** (`src/core/valuation/wacc.py`).
  Path A: Damodaran total ERP (recommended for CO/MX/CL/PE/BR).
  Path B: Decomposable mature ERP + CRP + FX risk (for AR, VE, hyperinflationary).
  Validator prevents double-counting between paths.
- **DCF extensions** (`src/core/valuation/dcf_extensions.py`).
  Three terminal value methods: Gordon Growth (standard), Normalized (cyclical),
  Two-Stage (capex-heavy businesses with negative early FCFs).
  Auto-detection picks the right method based on FCF stability.
- **Comparables module** (`src/core/comparables/bigfour.py`) — heuristic parser
  for McKinsey-style DCF reports + side-by-side comparison.
- **7 API endpoints** — health, WACC, DCF, macro, EMBI Latam (per-country + listing).
- **Ecopetrol integration test** (`tests/integration/test_ecopetrol_vs_sellside.py`).
  Validates our WACC and DCF against Bancolombia Equity Research Dec 2023.
  Results: WACC delta 0.33pp; DCF target within 7% of sell-side.
- **YPF integration test** (`tests/integration/test_ypf_vs_sellside.py`).
  Documents the Path B WACC for hyperinflationary economy + DCF limitation
  for resource companies. Honest about where DCF falls short.
- **Latam country expansion** — Mexico, Chile, Brazil, Peru added to Country enum
  with calibrated Damodaran defaults.

### Changed
- WACC model no longer double-counts Damodaran total ERP with separate CRP
  (validation now prevents this user error).
- Documentation expanded with full methodology lineage (USB-extracted PDFs in
  `docs/source/`).

### Anti-overfitting discipline
- All WACC/DCF improvements are general (work for any country/industry).
- YPF test documents DCF limitation rather than patching for YPF specifically.
- No company-specific parameters exist in core modules.

### Tests
- 67 passing (up from 48): 14 new unit tests, 2 new integration tests, 3 new country-expansion tests.
- No regressions.

## [0.1.0] - 2026-11-25

### Added
- Initial release of latam-valuation-engine.
- Vectorized Monte Carlo DCF (port of VBA from `PlaneaciónFra CANVAS.xlsm`).
- WACC with country risk premium adjustment.
- Macro snapshots (Damodaran + World Bank 2025/2026 data).
- FastAPI app with 4 endpoints.
- GitHub Actions CI (Python 3.11/3.12 + Docker smoke).
- GitHub Pages landing page.
- 34 tests passing.

[0.2.0]: https://github.com/AndresGM7/latam-valuation-engine/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AndresGM7/latam-valuation-engine/releases/tag/v0.1.0
