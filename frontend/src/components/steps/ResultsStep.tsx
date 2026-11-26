/**
 * Step 10 — Results.
 *
 * Shows the DCF response from the backend:
 *   - WACC breakdown
 *   - VPN mean / p05 / p50 / p95
 *   - Prob(VPN>0), Prob(TIR>WACC)
 *   - Sensitivity tornado chart (Recharts)
 *   - 3 fit scores
 *
 * Optionally fetches /valuation/macro/{country} for context.
 */

import { useQuery } from "@tanstack/react-query";
import { useLocation, Link } from "react-router-dom";
import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "../../api/client";
import { Card, ProgressBar, StatTile } from "../ui";
import { computeAllFitScores, totalCapex } from "../../lib/wizardStore";
import type { BusinessModel } from "../../lib/wizardStore";
import type { DCFResponse } from "../../api/client";

interface LocationState {
  dcf: DCFResponse;
  model: BusinessModel;
}

export function ResultsStep() {
  const location = useLocation();
  const state = location.state as LocationState | null;

  const fits = useMemo(
    () => (state ? computeAllFitScores(state.model) : []),
    [state],
  );

  const macro = useQuery({
    queryKey: ["macro", state?.model.country],
    queryFn: () => api.getMacro(state!.model.country),
    enabled: Boolean(state),
    retry: 0,
  });

  // DCFResponse from the backend only carries the rolled-up WACC%.
  // Fetch /wacc in parallel for the full component breakdown.
  const wacc = useQuery({
    queryKey: ["wacc", state?.model.country, state?.model.beta_unlevered],
    queryFn: () =>
      api.computeWacc({
        country: state!.model.country,
        beta_unlevered: state!.model.beta_unlevered,
        debt_to_total_capital_pct: 30,
      }),
    enabled: Boolean(state),
    retry: 0,
  });

  if (!state) {
    return (
      <div className="card p-6 text-center">
        <p className="text-navy-600">
          No hay resultados todavía. Vuelve al paso 9 para calcular la
          valoración.
        </p>
        <Link to="/review" className="btn-primary mt-4">
          Ir al paso de revisión
        </Link>
      </div>
    );
  }

  const { dcf, model } = state;

  // Sensitivity tornado: pivot ±x on each input and recompute the
  // simplified VPN = sum(FCF_t / (1+wacc)^t) - inversion_inicial.
  const baseFlows = dcf.flujos_base;
  const baseWacc = dcf.wacc_pct / 100;
  const baseInv = dcf.flujos_base[0] !== undefined ? 0 : 0;

  const computeVpn = (flows: number[], wacc: number, inv: number) => {
    let vpn = -inv;
    for (let t = 0; t < flows.length; t++) {
      vpn += flows[t] / Math.pow(1 + wacc, t + 1);
    }
    return vpn;
  };

  const baseVpn = computeVpn(baseFlows, baseWacc, baseInv);

  const tornado = useMemo(() => {
    const waccUp = computeVpn(baseFlows, baseWacc + 0.02, baseInv) - baseVpn;
    const waccDn = computeVpn(baseFlows, baseWacc - 0.02, baseInv) - baseVpn;
    const revUp =
      computeVpn(baseFlows.map((f) => f * 1.1), baseWacc, baseInv) - baseVpn;
    const revDn =
      computeVpn(baseFlows.map((f) => f * 0.9), baseWacc, baseInv) - baseVpn;
    const costUp =
      computeVpn(
        baseFlows.map((f) => f - baseFlows[0] * 0.1),
        baseWacc,
        baseInv,
      ) - baseVpn;
    const costDn =
      computeVpn(
        baseFlows.map((f) => f + baseFlows[0] * 0.1),
        baseWacc,
        baseInv,
      ) - baseVpn;

    return [
      {
        variable: "WACC +200 bps",
        delta: Number(waccUp.toFixed(2)),
      },
      {
        variable: "WACC -200 bps",
        delta: Number(waccDn.toFixed(2)),
      },
      {
        variable: "Revenue +10%",
        delta: Number(revUp.toFixed(2)),
      },
      {
        variable: "Revenue -10%",
        delta: Number(revDn.toFixed(2)),
      },
      {
        variable: "Costos +10%",
        delta: Number(costUp.toFixed(2)),
      },
      {
        variable: "Costos -10%",
        delta: Number(costDn.toFixed(2)),
      },
    ].sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));
  }, [baseFlows, baseWacc, baseVpn, baseInv]);

  return (
    <div>
      <div className="mb-8">
        <div className="text-xs font-mono uppercase tracking-wider text-navy-500 mb-2">
          Paso 10 de 10
        </div>
        <h1 className="section-title">
          Resultados de valoración — {model.business_name}
        </h1>
        <p className="section-subtitle max-w-2xl">
          DCF Monte Carlo ({dcf.n_iterations.toLocaleString()} iteraciones) con
          WACC país-específico ({model.country}).
        </p>
      </div>

      {/* Top stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatTile
          label="VPN mean"
          value={`$${dcf.vpn_mean.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          hint={`p05/p50/p95: $${dcf.vpn_p05.toFixed(0)} / $${dcf.vpn_p50.toFixed(0)} / $${dcf.vpn_p95.toFixed(0)}`}
          tone={dcf.vpn_mean >= 0 ? "accent" : "navy"}
        />
        <StatTile
          label="WACC"
          value={`${dcf.wacc_pct.toFixed(2)}%`}
          hint={`Ke: ${dcf.cost_of_equity_pct.toFixed(2)}%`}
        />
        <StatTile
          label="P(VPN > 0)"
          value={`${(dcf.prob_vpn_positivo * 100).toFixed(1)}%`}
          hint={`P(TIR > WACC): ${(dcf.prob_tir_supera_wacc * 100).toFixed(1)}%`}
        />
        <StatTile
          label="TIR proyecto (mean)"
          value={`${dcf.tir_proyecto_mean.toFixed(2)}%`}
          hint={`TIR inversionista: ${dcf.tir_inversionista_mean.toFixed(2)}%`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card
          title="WACC breakdown"
          subtitle="Componentes país-específicos (de /api/v1/valuation/wacc)"
        >
          {wacc.isLoading && (
            <p className="text-sm text-navy-500">Cargando WACC…</p>
          )}
          {wacc.data && (
            <table className="w-full text-sm">
              <tbody>
                {Object.entries({
                  WACC: `${wacc.data.wacc_pct.toFixed(2)}%`,
                  "Cost of equity (Ke)": `${wacc.data.cost_of_equity_pct.toFixed(2)}%`,
                  "Cost of debt (after tax)": `${wacc.data.cost_of_debt_after_tax_pct.toFixed(2)}%`,
                  "CRP aplicado": `${wacc.data.country_risk_premium_applied_pct.toFixed(2)}%`,
                  ...Object.fromEntries(
                    Object.entries(wacc.data.components).map(([k, v]) => [
                      k,
                      typeof v === "number" ? v.toFixed(3) : String(v),
                    ]),
                  ),
                }).map(([k, v]) => (
                  <tr key={k} className="border-b border-navy-50 last:border-0">
                    <td className="py-1.5 text-navy-600">{k}</td>
                    <td className="py-1.5 font-mono text-right text-navy-900">
                      {v}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {wacc.isError && (
            <p className="text-xs text-red-600">
              No se pudo cargar el desglose de WACC. Mostrando sólo los
              valores de /dcf.
            </p>
          )}
        </Card>

        <Card
          title="DCF projection"
          subtitle={`Flujos base (${dcf.flujos_base.length} años)`}
        >
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-navy-500 tracking-wider border-b border-navy-100">
                <th className="py-2">Año</th>
                <th className="py-2 text-right">FCF base</th>
              </tr>
            </thead>
            <tbody>
              {dcf.flujos_base.map((f, idx) => (
                <tr key={idx} className="border-b border-navy-50 last:border-0">
                  <td className="py-1.5 font-mono">Y{idx + 1}</td>
                  <td
                    className={`py-1.5 font-mono text-right ${
                      f < 0 ? "text-red-600" : "text-navy-900"
                    }`}
                  >
                    ${f.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                </tr>
              ))}
              <tr className="border-t border-navy-200 font-medium">
                <td className="py-2 text-navy-700">CAPEX (inversion inicial)</td>
                <td className="py-2 font-mono text-right">
                  ${totalCapex(model).toLocaleString()}
                </td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>

      {/* Tornado chart */}
      <Card
        title="Sensitivity tornado"
        subtitle="Impacto en VPN ante ±x en cada variable (cliente)."
        className="mb-6"
      >
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <BarChart
              layout="vertical"
              data={tornado}
              margin={{ top: 16, right: 24, left: 96, bottom: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e7eb" />
              <XAxis type="number" stroke="#7b8794" fontSize={11} />
              <YAxis
                type="category"
                dataKey="variable"
                stroke="#7b8794"
                fontSize={11}
                width={92}
              />
              <Tooltip
                contentStyle={{
                  fontSize: 12,
                  border: "1px solid #cbd2d9",
                  borderRadius: 4,
                }}
                formatter={(v: number) => `$${v.toLocaleString()}`}
              />
              <Bar dataKey="delta" radius={[0, 4, 4, 0]}>
                {tornado.map((entry, idx) => (
                  <Cell
                    key={idx}
                    fill={entry.delta >= 0 ? "#10b981" : "#1f2933"}
                  />
                ))}
                <LabelList
                  dataKey="delta"
                  position="right"
                  formatter={(v: number) =>
                    `${v >= 0 ? "+" : ""}${v.toFixed(0)}`
                  }
                  fontSize={10}
                  fill="#1f2933"
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Fit scores */}
      <Card title="Encaje (3 tipos)" className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {fits.map((fit) => (
            <div key={fit.fit_type}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-navy-800">
                  {fit.fit_type === "problem_solution"
                    ? "Problema-Solución"
                    : fit.fit_type === "product_market"
                      ? "Producto-Mercado"
                      : "Modelo de Negocio"}
                </span>
                <span className="badge-navy">{fit.confidence}</span>
              </div>
              <ProgressBar
                value={fit.score}
                tone={
                  fit.score >= 70
                    ? "accent"
                    : fit.score >= 40
                      ? "amber"
                      : "red"
                }
              />
              <ul className="mt-3 space-y-1 text-xs text-navy-600">
                {fit.notes.slice(0, 3).map((n, i) => (
                  <li key={i}>— {n}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Card>

      {/* Macro context */}
      {macro.data && (
        <Card
          title={`Macro snapshot (${macro.data.country})`}
          subtitle={macro.data.source}
          className="mb-6"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatTile
              label="Inflación YoY"
              value={`${macro.data.inflation_yoy_pct.toFixed(1)}%`}
            />
            <StatTile
              label="EMBI spread"
              value={`${macro.data.embi_spread_bps.toFixed(0)} bps`}
            />
            <StatTile
              label="CRP"
              value={`${macro.data.country_risk_premium_pct.toFixed(2)}%`}
            />
            <StatTile
              label="GDP growth"
              value={`${macro.data.gdp_growth_yoy_pct.toFixed(1)}%`}
            />
          </div>
        </Card>
      )}
      {macro.isError && (
        <p className="text-xs text-navy-400 italic mb-6">
          No se pudo cargar el macro snapshot (endpoint opcional).
        </p>
      )}

      <div className="flex gap-3 justify-end">
        <Link to="/review" className="btn-secondary">
          Volver a revisión
        </Link>
        <Link to="/welcome" className="btn-primary">
          Reiniciar wizard
        </Link>
      </div>
    </div>
  );
}
