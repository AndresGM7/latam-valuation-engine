# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-25

### Added
- Vectorized Monte Carlo DCF engine with triangular distributions (port from VBA `Module1.TRIANGULAR` + `Module2.SIMULACION`).
- WACC with country risk premium for Colombia, Argentina, and US.
- REST API (FastAPI) with 4 endpoints: `POST /valuation/dcf`, `POST /valuation/wacc`, `GET /valuation/macro/{country}`, `GET /health`.
- Macro data layer (YAML) for Colombia and Argentina with current Banrep/DANE/BCRA/INDEC snapshots.
- Pydantic schemas with strict input validation.
- 31 unit tests passing in ~4s.
- Static landing page (`landing/index.html`).
- GitHub Actions CI: tests on Python 3.11/3.12, Docker smoke test, GitHub Pages deploy.
- Original VBA modules preserved in `docs/vba_original/` for credit and audit.
- Comprehensive `README.md` with thesis-driven positioning for Big 4 / Latam analysts.
- Methodology document at `docs/methodology.md`.

### Notes
- This is the first public release. It is feature-complete for the core DCF + WACC use case but does not yet include the CANVAS wizard UI, PDF report generation, or Stripe/Lemon Squeezy payment integration (planned for v0.2.0).
- The original Excel workbook (`PlaneacionFra_CANVAS_original.xlsm`) is included in `docs/assets/` for reference. The PDF workshop (28 MB) is not bundled; see `docs/assets/Workshop_Original_README.md` for the content summary.
