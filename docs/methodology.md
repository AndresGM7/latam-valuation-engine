# Methodology

How this engine builds a DCF, line by line.

## 1. WACC with country risk

The standard textbook WACC:

```
WACC = ke · (E/V) + kd · (1 − t) · (D/V)
```

For Latam, this is incomplete. We add a **country risk premium** to the
cost of equity:

```
ke = rf + β · ERP + CRP
```

Where:

| Variable | Meaning | Source (CO 2026) | Source (AR 2026) |
|----------|---------|------------------|------------------|
| `rf` | Risk-free rate (US 10Y proxy) | 4.30% | 4.30% |
| `β` | Levered beta (Hamada) | user input | user input |
| `ERP` | Equity risk premium (Damodaran) | 5.50% | 8.00% |
| `CRP` | Country risk premium (EMBI) | 2.80% | 8.50% |

**The country risk premium alone accounts for 30-60% of valuation
differences between US and Latam businesses.** Most off-the-shelf
SaaS tools ignore it. This engine doesn't.

## 2. Triangular Monte Carlo

Why triangular?

For a normal distribution you need mean + variance from historical
data. For early-stage SMEs, you don't have 30 years of revenue. You
have:

- **A pessimistic scenario** (the bear case from your last committee)
- **A probable scenario** (your base case)
- **An optimistic scenario** (the bull case)

This is exactly what the triangular distribution captures:

```
if R < (b−a)/(c−a):
    X = a + √(R · (c−a) · (b−a))
else:
    X = c − √((1−R) · (c−a) · (c−b))
```

That's the formula in the original VBA `Module1.TRIANGULAR()`. We
port it to NumPy vectorization: 100,000 iterations in ~120ms.

## 3. Free Cash Flow → VPN

```
FCF_year_n = (Revenue_year_n − Costs_year_n) · (1 − tax)
VPN = Σ FCF_year_n / (1 + WACC)^n − Initial_Investment
```

We expose `VPN_mean`, `VPN_p05`, `VPN_p50`, `VPN_p95`, and
`P(VPN > 0)`. The probability of success is what matters for an
investment committee, not the point estimate.

## 4. Sources of truth

Every default is documented in `data/macro/{country}.yaml`. Each field
has a `source` string naming the public origin (Banrep, DANE, BCRA,
INDEC, J.P. Morgan EMBI, Damodaran).

We do NOT scrape these endpoints live — that's a v2 feature. For now,
quarterly manual refresh is the standard practice at tier-1 consulting
firms for any Latam valuation engagement.

## 5. Original VBA → Python port

| Original (VBA / XLSM) | New (Python) |
|-----------------------|--------------|
| `Module1.TRIANGULAR()` | `core.distributions.triangular_sample` |
| `Module2.SIMULACION()` loop | `core.valuation.run_monte_carlo` (vectorized) |
| Excel `PMT()` for amortización | `core.financiero.credito.cuota()` |
| Excel `=RAND()*(max-min)+min` | `numpy.random.uniform` |
| Excel cell ranges | Pydantic models |
| Hardcoded macros | CLI / API |

The original VBA modules are preserved in `docs/vba_original/` for
auditability and to give credit where due.
