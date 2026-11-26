/**
 * Step 9 — Review + submit.
 *
 * Shows the computed fit scores and a summary of the canvas, then sends
 * everything to the FastAPI backend (WACC + DCF) when the user clicks
 * "Calcular valoración". The backend response is forwarded to the
 * Results step via React Router state.
 */

import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useMemo } from "react";

import {
  Card,
  ProgressBar,
  StepHeader,
  WizardFooter,
  StatTile,
} from "../ui";
import {
  useWizard,
  computeAllFitScores,
  projectCashFlows,
  totalCapex,
  totalOpex,
} from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";
import { api, type DCFResponse } from "../../api/client";

export function ReviewStep({ goBack }: StepProps) {
  const { state, dispatch } = useWizard();
  const navigate = useNavigate();

  // Compute fit scores client-side (mirror of src/core/canvas/model.py)
  const fits = useMemo(() => computeAllFitScores(state), [state]);
  // Sync into store so Results step + macros can read them
  if (
    JSON.stringify(state.fit_scores) !== JSON.stringify(fits) &&
    fits.length > 0
  ) {
    dispatch({ type: "SET_FIT_SCORES", payload: fits });
  }

  const projection = useMemo(() => projectCashFlows(state), [state]);
  const yearOneRev = projection[0]?.revenue ?? 0;
  const tam = yearOneRev * 100; // naive TAM multiplier
  const sam = yearOneRev * 10;
  const som = yearOneRev * 1;

  const dcfMutation = useMutation<DCFResponse, Error>({
    mutationFn: async () => {
      const flujos = projection.map((p) =>
        Number((p.free_cash_flow / 1000).toFixed(2)),
      );
      if (flujos.every((f) => f === 0)) {
        throw new Error(
          "Tus flujos de caja son todos cero. Ajusta los streams de ingreso o los costos antes de enviar.",
        );
      }

      // WACC first (so we have wacc_pct available) — but the backend
      // already does this internally inside /dcf, so we just hit /dcf.
      // We also call /wacc in parallel in the results page to get the
      // full component breakdown.
      return api.computeDcf({
        country: state.country,
        flujos_base: flujos,
        inversion_inicial: Number((totalCapex(state) / 1000).toFixed(2)),
        beta_unlevered: state.beta_unlevered,
        debt_to_total_capital_pct: 30,
        n_iterations: 5000,
        growth_revenue_pesimista: -5,
        growth_revenue_probable: 8,
        growth_revenue_optimista: 20,
        growth_costs_pesimista: 3,
        growth_costs_probable: 5,
        growth_costs_optimista: 10,
        seed: 42,
      });
    },
    onSuccess: (resp) => {
      navigate("/results", { state: { dcf: resp, model: state } });
    },
  });

  return (
    <div>
      <StepHeader
        step={9}
        total={10}
        title="Revisión y encaje"
        subtitle="Resumen del CANVAS + score automático de los 3 tipos de fit. Al hacer clic en 'Calcular valoración', los flujos se envían al motor DCF Monte Carlo."
      />

      <Card
        title="Encaje (3 tipos)"
        subtitle="Calculado a partir de jobs/pains/gains, channels, revenue streams y costos."
        className="mb-6"
      >
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
                <span
                  className={`badge ${
                    fit.confidence === "high"
                      ? "bg-accent-50 text-accent-700"
                      : fit.confidence === "medium"
                        ? "bg-amber-50 text-amber-700"
                        : "bg-red-50 text-red-700"
                  }`}
                >
                  {fit.confidence}
                </span>
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
                {fit.notes.slice(0, 4).map((n, i) => (
                  <li key={i} className="leading-snug">
                    — {n}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Card>

      <Card
        title="Resumen financiero (proyección determinística)"
        subtitle="Cálculo local — el backend corre Monte Carlo con estos mismos flujos base."
        className="mb-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <StatTile
            label="TAM (naive x100)"
            value={`$${Math.round(tam).toLocaleString()}`}
            hint="Total addressable market (supuesto)"
          />
          <StatTile
            label="SAM (naive x10)"
            value={`$${Math.round(sam).toLocaleString()}`}
            hint="Serviceable addressable market"
          />
          <StatTile
            label="SOM (año 1)"
            value={`$${Math.round(som).toLocaleString()}`}
            hint="Serviceable obtainable market"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatTile
            label="CAPEX total"
            value={`$${totalCapex(state).toLocaleString()}`}
          />
          <StatTile
            label="OPEX anual"
            value={`$${totalOpex(state).toLocaleString()}`}
          />
          <StatTile
            label="Revenue año 1"
            value={`$${Math.round(yearOneRev).toLocaleString()}`}
          />
        </div>
      </Card>

      <Card
        title={`Listo para valoración DCF — ${state.business_name || "(sin nombre)"}`}
        subtitle={`País: ${state.country}. Beta: ${state.beta_unlevered}. Horizonte: ${state.horizon_years}y.`}
        className="mb-6"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-navy-500 tracking-wider border-b border-navy-100">
                <th className="py-2">Año</th>
                <th className="py-2">Revenue</th>
                <th className="py-2">Costos</th>
                <th className="py-2">FCF</th>
              </tr>
            </thead>
            <tbody>
              {projection.map((p) => (
                <tr key={p.year} className="border-b border-navy-50">
                  <td className="py-2 font-mono">Y{p.year}</td>
                  <td className="py-2 font-mono">
                    ${Math.round(p.revenue).toLocaleString()}
                  </td>
                  <td className="py-2 font-mono">
                    ${Math.round(p.costs).toLocaleString()}
                  </td>
                  <td
                    className={`py-2 font-mono ${
                      p.free_cash_flow < 0 ? "text-red-600" : "text-accent-700"
                    }`}
                  >
                    ${Math.round(p.free_cash_flow).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {dcfMutation.isError && (
        <div className="card p-4 mb-6 border-red-200 bg-red-50/40">
          <p className="text-sm text-red-700">
            Error: {dcfMutation.error.message}
          </p>
          <p className="text-xs text-red-600 mt-1">
            Verifica que el backend esté corriendo en http://localhost:8000.
          </p>
        </div>
      )}

      <WizardFooter
        onBack={goBack}
        onNext={() => dcfMutation.mutate()}
        nextLabel={
          dcfMutation.isPending ? "Calculando..." : "Calcular valoración"
        }
        nextDisabled={dcfMutation.isPending}
      />
    </div>
  );
}
