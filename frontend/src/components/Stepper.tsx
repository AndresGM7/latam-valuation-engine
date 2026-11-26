/**
 * Top-of-page stepper for the 10-step wizard.
 * Shows: pending / active / completed states with a connecting rail.
 */

import { clsx } from "clsx";

export interface StepMeta {
  id: number;
  label: string;
  short: string;
}

export const WIZARD_STEPS: StepMeta[] = [
  { id: 1, label: "Bienvenida y metodología", short: "Inicio" },
  { id: 2, label: "Segmentos de cliente", short: "Clientes" },
  { id: 3, label: "Propuesta de valor", short: "Propuesta" },
  { id: 4, label: "Canales", short: "Canales" },
  { id: 5, label: "Fuentes de ingreso", short: "Ingresos" },
  { id: 6, label: "Recursos, actividades, socios", short: "Recursos" },
  { id: 7, label: "Estructura de costos", short: "Costos" },
  { id: 8, label: "Experimentos", short: "Experimentos" },
  { id: 9, label: "Revisión y encaje", short: "Revisión" },
  { id: 10, label: "Resultados DCF", short: "Resultados" },
];

export function Stepper({ current }: { current: number }) {
  return (
    <nav aria-label="Progreso del wizard" className="w-full">
      <ol className="hidden md:flex items-center w-full gap-1">
        {WIZARD_STEPS.map((step, idx) => {
          const isComplete = step.id < current;
          const isActive = step.id === current;
          return (
            <li
              key={step.id}
              className="flex-1 flex items-center"
              aria-current={isActive ? "step" : undefined}
            >
              <div className="flex flex-col items-center min-w-0">
                <div
                  className={clsx(
                    "w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold border",
                    isComplete &&
                      "bg-navy-900 text-white border-navy-900",
                    isActive &&
                      "bg-white text-navy-900 border-navy-900 ring-2 ring-navy-200",
                    !isComplete &&
                      !isActive &&
                      "bg-white text-navy-400 border-navy-200",
                  )}
                >
                  {isComplete ? (
                    <svg
                      className="w-3.5 h-3.5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.7 5.3a1 1 0 010 1.4l-8 8a1 1 0 01-1.4 0l-4-4a1 1 0 011.4-1.4L8 12.6l7.3-7.3a1 1 0 011.4 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    step.id
                  )}
                </div>
                <span
                  className={clsx(
                    "mt-1.5 text-[11px] font-medium truncate max-w-[90px] text-center",
                    isActive ? "text-navy-900" : "text-navy-500",
                  )}
                >
                  {step.short}
                </span>
              </div>
              {idx < WIZARD_STEPS.length - 1 && (
                <div
                  className={clsx(
                    "flex-1 h-0.5 mx-1 mb-5",
                    isComplete ? "bg-navy-900" : "bg-navy-200",
                  )}
                />
              )}
            </li>
          );
        })}
      </ol>

      {/* Mobile compact indicator */}
      <div className="md:hidden">
        <div className="text-xs font-mono uppercase tracking-wider text-navy-500">
          Paso {current} de {WIZARD_STEPS.length}
        </div>
        <div className="mt-2 h-1.5 w-full bg-navy-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-navy-900 transition-all"
            style={{ width: `${(current / WIZARD_STEPS.length) * 100}%` }}
          />
        </div>
        <div className="mt-2 text-sm font-medium text-navy-900">
          {WIZARD_STEPS[current - 1]?.label}
        </div>
      </div>
    </nav>
  );
}
