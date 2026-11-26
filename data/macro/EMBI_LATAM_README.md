# EMBI Global Diversified — Historical Series (Latam)

**Source**: Banco Central de la República Dominicana (BCRD)
**URL**: https://www.bancentral.gov.do/a/d/2585-entorno-internacional
**File**: `EMBI_Latam_BCRD.xlsx`
**Coverage**: 2007-10-29 to present (daily, business days)
**Countries**: 18 Latam countries + Global + LATINO aggregate

## What this is

The Emerging Markets Bond Index Global (EMBI) Diversified sub-indices, expressed
as spreads over US Treasury bonds (in percentage points, e.g. `2.61` = 261 bps).

This is the **gold-standard measure of sovereign credit risk** for emerging
markets, used by:
- JP Morgan (index publisher)
- World Bank / IMF (macro risk monitoring)
- Big 4 consulting firms (country risk premium in DCF)
- Sovereign wealth funds (asset allocation)

## Why this matters for our WACC

The country risk premium (CRP) added to the cost of equity is mathematically
related to the EMBI spread:

    CRP ≈ EMBI_spread × (σ_equity / σ_bond)

Where σ_equity and σ_bond are local volatilities. Damodaran publishes an
updated version of this formula quarterly.

For our engine, we use the **last 30-day moving average** of EMBI as the
authoritative proxy for country risk, falling back to Damodaran's CRP when
the country is not in this dataset.

## Coverage

Last data point at time of capture: **2026-11-24**

| Country | Code | Last EMBI (%) | 30d avg |
|---------|------|--------------:|--------:|
| Global   | GBL  | 2.28 | 2.05 |
| LATINO   | LAT  | 2.31 | 2.06 |
| Rep. Dom.| DOM  | 2.08 | 1.90 |
| Argentina| ARG  | 10.92 | 8.05 |
| Bolivia  | BOL  | 5.91 | 5.11 |
| Brasil   | BRA  | 2.15 | 1.88 |
| Chile    | CHL  | 1.14 | 1.02 |
| Colombia | COL  | 2.61 | 2.32 |
| Costa Rica| CRI | 1.68 | 1.53 |
| Ecuador  | ECU  | 6.31 | 5.68 |
| El Salvador| SLV | 3.37 | 3.11 |
| Guatemala| GTM  | 1.55 | 1.39 |
| Honduras | HND  | 2.17 | 1.98 |
| México   | MEX  | 2.47 | 2.25 |
| Paraguay | PRY  | 1.45 | 1.31 |
| Perú     | PER  | 1.36 | 1.21 |
| Panamá   | PAN  | 1.44 | 1.32 |
| Uruguay  | URY  | 0.93 | 0.83 |
| Venezuela| VEN  | 47.11 | 46.38 |

## License

The BCRD publishes this dataset as a public good for academic and financial
research. The data is in the public domain.
