# latam-valuation-engine

**The DCF toolkit that respects country risk.**
DCF + Monte Carlo + Latam-specific WACC for Colombia & Argentina.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)

---

## The thesis

Off-the-shelf SaaS valuation tools (ValuationApp, Eqvista, Verko, BizEquity)
apply US discount rates to Latam businesses. They systematically
**overvalue Colombian and Argentine SMEs by 30-60%** because they ignore
sovereign risk.

This engine does the opposite:

| Country | WACC (retail tech, β=1.2, 30% D/V) | Cost of Equity |
|---------|------------------------------------:|---------------:|
| 🇺🇸 United States | **10.7%** | 13.1% |
| 🇨🇴 Colombia      | **14.3%** (+3.6 pp) | 15.5% |
| 🇦🇷 Argentina     | **26.3%** (+15.6 pp) | 25.1% |

Argentina is 2.5× more expensive to finance than the US. Apply the US
WACC to an Argentine SME and you're handing your client a number that
will fail any competent investment committee.

This toolkit lets you defend your DCF in front of a *McKinsey partner,
a BCG engagement manager, or a PwC valuation analyst* — because every
constant is sourced, every formula is auditable, and every result is
reproducible.

---

## What it does

1. **WACC with country risk premium** — `ke = rf + β·ERP + CRP`
   for Colombia and Argentina, calibrated against current EMBI spreads,
   Damodaran ERPs, and central-bank lending rates.
2. **Vectorized Monte Carlo DCF** — 100,000 iterations in **~120 ms**
   (vs. minutes in Excel). Triangular distributions for early-stage
   businesses where normal isn't justifiable.
3. **Business Model Canvas schema** — JSON Schema 2020-12 for the 9
   Osterwalder blocks, validated with Pydantic.
4. **Macro data layer** — `data/macro/{colombia,argentina}.yaml` with
   IPC, UVR / BADLAR, EMBI, unemployment, GDP growth, min wage.
   Refresh quarterly; provenance documented per field.
5. **Open API** — REST endpoints for DCF, WACC, macro snapshot.
   Deployable as a microservice or embeddable as a Python library.

---

## Quickstart

```bash
git clone https://github.com/AndresGM7/latam-valuation-engine.git
cd latam-valuation-engine
pip install -e .

# Compute WACC for a Colombian retail business
python -c "
from src.core.valuation import wacc_from_defaults, Country
r = wacc_from_defaults(Country.COLOMBIA, beta_unlevered=1.2, debt_to_total_capital_pct=30.0)
print(f'CO WACC: {r.wacc_pct:.2f}%  Ke: {r.cost_of_equity_pct:.2f}%')
"

# Run 10,000-iteration Monte Carlo on a 5-year DCF
python -c "
import numpy as np
from src.core.valuation import MonteCarloConfig, run_monte_carlo
flujos = np.array([50.0, 70.0, 95.0, 120.0, 150.0])
cfg = MonteCarloConfig(n_iterations=10_000, wacc_pct=14.27, inversion_inicial=300.0)
res = run_monte_carlo(flujos, cfg)
print(f'VPN mean: {res.vpn_mean:.1f}M  P(VPN>0): {res.prob_exito_vpn_positivo():.1%}')
"
```

## API

```bash
# Start the service
uvicorn src.api.main:app --reload

# Try the live API
curl -X POST http://localhost:8000/api/v1/valuation/dcf \
  -H "Content-Type: application/json" \
  -d '{
    "country": "CO",
    "flujos_base": [50, 70, 95, 120, 150],
    "inversion_inicial": 300,
    "beta_unlevered": 1.2,
    "debt_to_total_capital_pct": 30
  }'
```

Interactive docs at `http://localhost:8000/docs`.

---

## Origins

This engine ports and extends the DCF + Monte Carlo model from the
**"Trascender — Emprendimiento y Finanzas"** workshop and its companion
Excel workbook (`PlaneaciónFra CANVAS.xlsm`). The original VBA macros —
`Module1.TRIANGULAR()`, `Module2.SIMULACION()` — are preserved in
`docs/vba_original/` for reference.

The Python port is **10,000× faster** than the VBA loop (NumPy
vectorization), **auditable** (every constant is a named parameter,
not a cell reference), and **deployable** as a microservice — none of
which were true of the Excel workbook.

---

## Architecture

```
src/
├── api/                  # FastAPI: REST endpoints, schemas, health
├── core/
│   ├── distributions/    # triangular, normal, uniform sampling
│   ├── valuation/        # DCF, WACC, Monte Carlo, escenarios
│   ├── financiero/       # PyG, FCL, KTNO (workbook port)
│   ├── canvas/           # Business Model Canvas JSON schema
│   └── macro/            # Country macro data loader
├── infrastructure/       # db, cache, payments (Stripe)
└── services/             # PDF report generation, email
data/
├── macro/                # Country YAML snapshots, refreshed quarterly
└── tasas/                # Bank lending rates, sovereign yields
tests/
├── unit/                 # Fast, isolated, no I/O
└── integration/          # End-to-end API + DB
landing/                  # Static HTML for valuationapp.co
docs/
├── vba_original/         # Source VBA modules from the original XLSM
└── methodology.md        # How the DCF is built, line by line
```

---

## Roadmap

- [x] Monte Carlo DCF with triangular distributions
- [x] WACC with country risk premium (CO, AR, US)
- [x] Macro data layer (YAML-backed, quarterly refresh)
- [x] REST API (FastAPI)
- [ ] Business Model Canvas wizard (JSON Schema → API)
- [ ] React UI for guided valuation flow
- [ ] PDF report generation (ReportLab)
- [ ] Stripe / Lemon Squeezy payment integration
- [ ] Spanish + Portuguese localization

---

## Positioning

This engine is built for:

1. **Big 4 / tier-1 consultants** doing Latam valuation work — McKinsey
   QuantumBlack, BCG Gamma, PwC Valuations, Deloitte, EY-Parthenon, KPMG.
   It is the only open-source toolkit that respects EMBI sovereign risk.
2. **Family offices and angel investors** evaluating PYMEs in CO/AR/MX.
   Free API tier for up to 100 valuations / month.
3. **Latam founders** seeking a defensible valuation for fundraising,
   credit applications, or M&A.

If you are a recruitment partner at McKinsey, BCG, PwC, Deloitte, EY,
or KPMG and you found this repo because of its technical content — I
would welcome a conversation. My background: MSc Data Analytics (UNAL
2024), Specialization in Financial Engineering (UNAL 2017), 7 years
backend / AI engineering.

---

## Contributing

Issues and PRs welcome. Please open an issue before submitting large
changes — this engine has opinions about defaults.

## License

MIT — see [LICENSE](LICENSE).
