/**
 * Step 8 — Experiments.
 *
 * Recommends Bland & Osterwalder experiments (S1 → S3) based on which
 * fit type has the weakest current evidence, and lets the user check
 * off which ones they intend to run.
 *
 * Mirrors src/core/canvas/experiments.py (recommend_experiments).
 */

import { useMemo } from "react";

import { Card, StepHeader, WizardFooter } from "../ui";
import { clsx } from "clsx";
import {
  useWizard,
  EXPERIMENT_LIBRARY,
  type ExperimentMeta,
} from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";

const COST_LABEL: Record<ExperimentMeta["cost"], string> = {
  free: "Gratis",
  low: "< $100",
  medium: "$100-$1k",
  high: "> $1k",
};

const STAGE_LABEL: Record<ExperimentMeta["stage"], string> = {
  discovery: "Descubrimiento",
  validation: "Validación",
  decide: "Decisión",
  scale: "Escalar",
};

const FIT_LABEL: Record<ExperimentMeta["fit_type"], string> = {
  problem_solution: "Problema-Solución",
  product_market: "Producto-Mercado",
  business_model: "Modelo de Negocio",
};

export function ExperimentsStep({ goNext, goBack }: StepProps) {
  const { state, dispatch } = useWizard();

  const recommended = useMemo<ExperimentMeta[]>(() => {
    const fits = state.fit_scores;
    if (fits.length === 0) {
      return EXPERIMENT_LIBRARY.filter(
        (e) => e.stage === "discovery" || e.stage === "validation",
      ).slice(0, 5);
    }
    const weakest = [...fits].sort((a, b) => a.score - b.score)[0];
    return EXPERIMENT_LIBRARY.filter((e) => e.fit_type === weakest.fit_type).slice(
      0,
      5,
    );
  }, [state.fit_scores]);

  const selected = new Set(state.experiments_run);

  const toggle = (id: string) => {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    dispatch({ type: "SET_EXPERIMENTS", payload: Array.from(next) });
  };

  return (
    <div>
      <StepHeader
        step={8}
        total={10}
        title="Experimentos (Bland & Osterwalder)"
        subtitle="Antes de invertir, valida. Selecciona los experimentos que vas a correr para gathering evidence del encaje más débil."
      />

      <Card
        title="Recomendados para ti"
        subtitle="Basado en tu encaje más débil (problem-solution, product-market o business-model)."
        className="mb-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommended.map((exp) => (
            <ExperimentCard
              key={exp.id}
              exp={exp}
              selected={selected.has(exp.id)}
              onToggle={() => toggle(exp.id)}
            />
          ))}
        </div>
        {recommended.length === 0 && (
          <p className="text-sm text-navy-500">
            Completa los pasos previos para recibir recomendaciones.
          </p>
        )}
      </Card>

      <Card title="Biblioteca completa" subtitle="Todos los experimentos disponibles">
        <div className="space-y-3">
          {EXPERIMENT_LIBRARY.map((exp) => (
            <ExperimentRow
              key={exp.id}
              exp={exp}
              selected={selected.has(exp.id)}
              onToggle={() => toggle(exp.id)}
            />
          ))}
        </div>
      </Card>

      <WizardFooter onBack={goBack} onNext={goNext} />
    </div>
  );
}

function ExperimentCard({
  exp,
  selected,
  onToggle,
}: {
  exp: ExperimentMeta;
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={clsx(
        "text-left card p-4 transition-all",
        selected
          ? "border-navy-900 ring-2 ring-navy-200 bg-navy-50/40"
          : "hover:border-navy-300",
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="font-mono text-xs text-navy-500">{exp.id}</div>
        <div
          className={clsx(
            "w-5 h-5 rounded border flex items-center justify-center text-xs",
            selected ? "bg-navy-900 border-navy-900 text-white" : "border-navy-300",
          )}
        >
          {selected && (
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-3 h-3">
              <path
                fillRule="evenodd"
                d="M16.7 5.3a1 1 0 010 1.4l-8 8a1 1 0 01-1.4 0l-4-4a1 1 0 011.4-1.4L8 12.6l7.3-7.3a1 1 0 011.4 0z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
      </div>
      <h3 className="font-semibold text-navy-900">{exp.name}</h3>
      <p className="text-xs text-navy-600 mt-1">{exp.description}</p>
      <div className="mt-3 flex flex-wrap gap-2 text-[10px] uppercase tracking-wider">
        <span className="badge-navy">{STAGE_LABEL[exp.stage]}</span>
        <span className="badge-navy">{FIT_LABEL[exp.fit_type]}</span>
        <span className="badge-navy">{COST_LABEL[exp.cost]}</span>
        <span className="badge-navy">{exp.duration_days}d</span>
        <span className="badge-navy">Evidencia {exp.evidence_strength}/5</span>
      </div>
    </button>
  );
}

function ExperimentRow({
  exp,
  selected,
  onToggle,
}: {
  exp: ExperimentMeta;
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={clsx(
        "w-full text-left p-3 rounded-md border transition-colors flex items-start gap-3",
        selected
          ? "border-navy-900 bg-navy-50/40"
          : "border-navy-100 hover:border-navy-300",
      )}
    >
      <div
        className={clsx(
          "mt-0.5 w-5 h-5 rounded border flex-shrink-0 flex items-center justify-center text-xs",
          selected ? "bg-navy-900 border-navy-900 text-white" : "border-navy-300",
        )}
      >
        {selected && (
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-3 h-3">
            <path
              fillRule="evenodd"
              d="M16.7 5.3a1 1 0 010 1.4l-8 8a1 1 0 01-1.4 0l-4-4a1 1 0 011.4-1.4L8 12.6l7.3-7.3a1 1 0 011.4 0z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </div>
      <div className="flex-1">
        <div className="flex items-baseline gap-2">
          <span className="font-mono text-xs text-navy-500">{exp.id}</span>
          <span className="font-medium text-navy-900">{exp.name}</span>
          <span className="text-xs text-navy-500">{exp.page_reference}</span>
        </div>
        <p className="text-xs text-navy-600 mt-0.5">{exp.description}</p>
        <div className="mt-1 flex flex-wrap gap-2 text-[10px] uppercase tracking-wider">
          <span className="badge-navy">{STAGE_LABEL[exp.stage]}</span>
          <span className="badge-navy">{FIT_LABEL[exp.fit_type]}</span>
          <span className="badge-navy">{COST_LABEL[exp.cost]}</span>
          <span className="badge-navy">{exp.duration_days}d</span>
        </div>
      </div>
    </button>
  );
}
