# latam-valuation-engine — CANVAS Wizard (frontend)

React + TypeScript single-page app that lets an entrepreneur walk through
the **Business Model Canvas + Value Proposition Design** and submit the
resulting cash flows to the FastAPI backend for a **Monte Carlo DCF
valuation with country-specific WACC** (Damodaran + EMBI).

The wizard follows the methodology in:

- Osterwalder & Pigneur (2010) *Business Model Generation* — 9 CANVAS blocks
- Osterwalder et al. (2014) *Value Proposition Design* — customer jobs / pains / gains ↔ products / pain relievers / gain creators
- Bland & Osterwalder (2019) *Testing Business Ideas* — library of 44 experiments and the **3 types of fit** (problem-solution / product-market / business-model)
- The *Planeación Financiera bajo CANVAS* methodology by Andrés Felipe Giraldo M. & Harold Mauricio Ramos P.

---

## Stack

| Layer        | Tech |
|--------------|------|
| Bundler      | Vite 5 |
| Framework    | React 18 + TypeScript 5 |
| Routing      | react-router-dom 6 |
| API state    | @tanstack/react-query 5 |
| Forms        | react-hook-form 7 + zod 3 + @hookform/resolvers |
| Styling      | TailwindCSS 3 (navy/grey McKinsey-style palette, Inter font) |
| Charts       | recharts 2 (sensitivity tornado) |

---

## Quick start

### Prerequisites

- Node.js ≥ 20 (developed on 22.23.1)
- npm ≥ 10
- The Python backend running locally on `http://localhost:8000` (see
  the repo's `README.md` — `uvicorn src.api.main:app --reload --port 8000`)

### Install + build

```bash
cd frontend
npm install
npm run build       # type-checks then bundles into dist/
```

### Dev (with backend proxy)

```bash
cd frontend
npm run dev         # serves http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000` (see
`vite.config.ts`). You can override the API base URL with the
`VITE_API_BASE_URL` env var.

### Type-check only

```bash
npm run typecheck
```

### One-shot build verification

A script that runs install + typecheck + build and prints the dist/
contents:

```bash
./build_check.sh           # POSIX (git-bash, mac, Linux)
./build_check.ps1          # Windows PowerShell
```

---

## Endpoints consumed

The frontend talks to **exactly** these FastAPI routes (no others are
invented):

| Method | Path                                   | Used in step |
|--------|----------------------------------------|--------------|
| GET    | `/api/v1/health`                       | (smoke check, optional) |
| POST   | `/api/v1/valuation/wacc`               | Review (indirectly) |
| POST   | `/api/v1/valuation/dcf`                | Review (submit) |
| GET    | `/api/v1/valuation/macro/{country}`    | Results (context) |

The TypeScript client lives in `src/api/client.ts` and is the single
source of truth for the request/response shapes.

> **Note on `POST /api/v1/valuation/wacc`:** the task description listed
> many optional fields (`cost_of_debt_pretax_pct`, `tax_rate_pct`,
> `equity_risk_premium_pct`, `country_risk_premium_pct`,
> `risk_free_rate_pct`). The current backend schema
> (`src/api/schemas/__init__.py :: WACCRequest`) only reads
> `country`, `beta_unlevered`, `debt_to_total_capital_pct`; the rest of
> the inputs are pulled server-side from `DEFAULTS_2026`. The client
> sends only those three fields to avoid spurious 422s. Once the
> backend grows, the client can be extended in one place
> (`src/api/client.ts`).

---

## 10-step wizard

Each step is its own file under `src/components/steps/` and is
mounted by `src/components/CanvasWizard.tsx` (which is itself just an
orchestrator + stepper).

| # | Component                  | Purpose |
|---|----------------------------|---------|
| 1 | `WelcomeStep.tsx`          | Identity (name, country, industry, beta) + methodology overview |
| 2 | `CustomerSegmentsStep.tsx` | Up to 3 segments × {jobs / pains / gains} with importance/satisfaction scoring |
| 3 | `ValuePropositionStep.tsx` | Headline, description, products, pain relievers, gain creators, alternatives |
| 4 | `ChannelsStep.tsx`         | Channels across awareness → evaluation → purchase → delivery → after-sales |
| 5 | `RevenueStreamsStep.tsx`   | Streams with ARPU, year-1 volume, growth |
| 6 | `KeyBlocksStep.tsx`        | Key resources (CAPEX), activities (OPEX), partners (cost) |
| 7 | `CostStructureStep.tsx`    | Fixed costs + variable % of revenue + computed CAPEX/OPEX summary |
| 8 | `ExperimentsStep.tsx`      | Recommended Bland experiments (S1-01 → S3-02) based on weakest fit |
| 9 | `ReviewStep.tsx`           | Computes 3 fit scores client-side, projects cash flows, calls `/api/v1/valuation/dcf` |
| 10 | `ResultsStep.tsx`         | DCF/WACC outputs + sensitivity tornado (Recharts) + macro snapshot |

---

## Project structure

```
frontend/
├── build_check.sh          # POSIX verification script
├── build_check.ps1         # Windows verification script
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
├── public/
│   └── favicon.svg
└── src/
    ├── App.tsx              # router + layout
    ├── main.tsx             # React entrypoint
    ├── index.css            # Tailwind + global styles
    ├── api/
    │   └── client.ts        # TypeScript client for the FastAPI backend
    ├── components/
    │   ├── CanvasWizard.tsx # orchestrator + stepper
    │   ├── Stepper.tsx      # progress indicator
    │   ├── ui.tsx           # shared primitives (ProgressBar, Card, Field, ...)
    │   └── steps/
    │       ├── WelcomeStep.tsx
    │       ├── CustomerSegmentsStep.tsx
    │       ├── ValuePropositionStep.tsx
    │       ├── ChannelsStep.tsx
    │       ├── RevenueStreamsStep.tsx
    │       ├── KeyBlocksStep.tsx
    │       ├── CostStructureStep.tsx
    │       ├── ExperimentsStep.tsx
    │       ├── ReviewStep.tsx
    │       └── ResultsStep.tsx
    └── lib/
        └── wizardStore.tsx  # React context + reducer + fit/financial helpers
```

---

## Deployment

The frontend is a static SPA — `npm run build` produces `dist/` with
`index.html` + hashed JS/CSS bundles.

### Option A — Netlify / Vercel / Cloudflare Pages

- Build command: `npm run build`
- Publish directory: `dist`
- Set `VITE_API_BASE_URL` to your FastAPI origin (or use the
  `/api` proxy in `vite.config.ts` if both are on the same domain).

### Option B — Same domain as the FastAPI backend (recommended)

Configure FastAPI (or a reverse proxy like Nginx / Caddy) to serve
`frontend/dist/` on `/` and forward `/api/*` to uvicorn. Example with
`uvicorn.mount`:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
# ... register your routers ...
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="ui")
```

### Option C — GitHub Pages

See the existing `landing/` directory in the repo for an example
single-page deploy via `gh-pages`. The wizard follows the same shape
but is much larger.

---

## Notes

- No emoji in the UI (per house style).
- Mobile-responsive (`grid-cols-1 md:grid-cols-2/3`).
- The Python CI in `.github/workflows/ci.yml` only tests Python — this
  frontend does **not** break that pipeline. A future PR could add a
  separate `frontend-ci` job that runs `npm run build`.
- The 3 fit scores are computed client-side using the same heuristics
  as `src/core/canvas/model.py :: compute_problem_solution_fit` and
  `compute_business_model_fit`. The frontend never trusts the wizard
  state to the backend — it only sends the projected cash-flow vector
  to `/api/v1/valuation/dcf`.
