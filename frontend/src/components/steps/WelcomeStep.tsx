/**
 * Step 1 — Welcome + methodology.
 *
 * Explains that the wizard implements:
 *   - Osterwalder & Pigneur's Business Model Canvas (2010)
 *   - Osterwalder et al.'s Value Proposition Design (2014)
 *   - Bland & Osterwalder's "Testing Business Ideas" experiment library (2019)
 *   - The "3 Types of Fit" scoring (problem-solution, product-market, business-model)
 *
 * And that, at the end, the canvas is translated into a Monte Carlo DCF
 * valuation with country-specific WACC (Damodaran + EMBI).
 */

import { StepHeader, WizardFooter, Card, TextField, NumberField } from "../ui";
import { useWizard } from "../../lib/wizardStore";

export interface StepProps {
  goNext: () => void;
  goBack?: () => void;
}

export function WelcomeStep({ goNext }: StepProps) {
  const { state, dispatch } = useWizard();
  const canContinue = state.business_name.trim().length > 0;

  return (
    <div>
      <StepHeader
        step={1}
        total={10}
        title="Bienvenida al CANVAS Wizard"
        subtitle="Una sesión estructurada de planeación financiera que traduce tu modelo de negocio en una valoración DCF Monte Carlo calibrada por país."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card title="1. Modelo de negocio" subtitle="Osterwalder & Pigneur (2010)">
          <p className="text-sm text-navy-600">
            Los 9 bloques del Business Model Canvas: segmentos, propuesta de valor,
            canales, relaciones, fuentes de ingreso, recursos clave, actividades
            clave, socios clave y estructura de costos.
          </p>
        </Card>
        <Card title="2. Propuesta de valor" subtitle="Osterwalder et al. (2014)">
          <p className="text-sm text-navy-600">
            El encaje entre los trabajos / pains / gains de tu cliente y los
            productos / pain relievers / gain creators de tu solución. Es el
            corazón del Value Proposition Design.
          </p>
        </Card>
        <Card
          title="3. Encaje + experimentos"
          subtitle="Bland & Osterwalder (2019)"
        >
          <p className="text-sm text-navy-600">
            3 tipos de encaje (problema-solución, producto-mercado, modelo de
            negocio) y la biblioteca de 44 experimentos para gathering evidence:
            customer interviews, concierge MVP, conjoint, etc.
          </p>
        </Card>
      </div>

      <Card title="Empecemos" subtitle="Datos básicos de tu emprendimiento">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TextField
            label="Nombre del negocio"
            value={state.business_name}
            onChange={(v) =>
              dispatch({
                type: "SET_IDENTITY",
                payload: { ...state, business_name: v },
              })
            }
            placeholder="Ej. Cafetal SAS"
            error={!canContinue ? "Requerido para continuar" : undefined}
          />
          <div>
            <label className="label">País</label>
            <select
              className="input"
              value={state.country}
              onChange={(e) =>
                dispatch({
                  type: "SET_IDENTITY",
                  payload: {
                    ...state,
                    country: e.target.value as typeof state.country,
                  },
                })
              }
            >
              <option value="CO">Colombia</option>
              <option value="AR">Argentina</option>
              <option value="US">Estados Unidos (baseline)</option>
            </select>
            <p className="mt-1 text-xs text-navy-500">
              Define el WACC país-específico (Damodaran + EMBI) que usará el motor.
            </p>
          </div>
          <TextField
            label="Industria"
            value={state.industry}
            onChange={(v) =>
              dispatch({
                type: "SET_IDENTITY",
                payload: { ...state, industry: v },
              })
            }
            placeholder="Ej. SaaS, F&B, Retail"
          />
          <NumberField
            label="Beta unlevered (industria)"
            value={state.beta_unlevered}
            onChange={(v) =>
              dispatch({
                type: "SET_IDENTITY",
                payload: { ...state, beta_unlevered: v },
              })
            }
            min={0.1}
            max={3}
            step={0.05}
            hint="Buscar en Damodaran por industria. Default: 1.0."
          />
          <NumberField
            label="Horizonte de proyección (años)"
            value={state.horizon_years}
            onChange={(v) =>
              dispatch({
                type: "SET_IDENTITY",
                payload: {
                  ...state,
                  horizon_years: Math.max(1, Math.min(20, Math.round(v))),
                },
              })
            }
            min={1}
            max={20}
            step={1}
            hint="Típicamente 5 años para una PYME."
          />
        </div>
      </Card>

      <WizardFooter onNext={goNext} nextDisabled={!canContinue} />
    </div>
  );
}
