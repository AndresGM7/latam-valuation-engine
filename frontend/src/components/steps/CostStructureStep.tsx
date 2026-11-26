/**
 * Step 7 — Cost Structure.
 *
 * Three levers: fixed costs, variable cost as % of revenue, plus the
 * opex already captured in key activities/partners (re-used for
 * projection).
 */

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Card, NumberField, StepHeader, WizardFooter } from "../ui";
import { useWizard, totalOpex, totalCapex } from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";

const costSchema = z.object({
  fixed_costs_usd_per_year: z.coerce.number().min(0).default(0),
  variable_costs_pct_of_revenue: z.coerce.number().min(0).max(100).default(0),
});

type CostForm = z.infer<typeof costSchema>;

export function CostStructureStep({ goNext, goBack }: StepProps) {
  const { state, dispatch } = useWizard();

  const { register, handleSubmit, formState, watch } = useForm<CostForm>({
    resolver: zodResolver(costSchema),
    defaultValues: {
      fixed_costs_usd_per_year: state.cost_structure.fixed_costs_usd_per_year,
      variable_costs_pct_of_revenue:
        state.cost_structure.variable_costs_pct_of_revenue,
    },
    mode: "onSubmit",
  });

  const onSubmit = handleSubmit((data) => {
    dispatch({ type: "SET_COST_STRUCTURE", payload: data });
    goNext();
  });

  const fixed = watch("fixed_costs_usd_per_year");
  const variable = watch("variable_costs_pct_of_revenue");

  return (
    <form onSubmit={onSubmit}>
      <StepHeader
        step={7}
        total={10}
        title="Estructura de costos"
        subtitle="Costos fijos + costos variables como % del ingreso. Más el opex/capex que ya capturaste en recursos / actividades / socios."
      />

      <Card className="mb-6" title="Costos directos">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <NumberField
            label="Costos fijos anuales"
            value={fixed}
            onChange={(v) => {
              register("fixed_costs_usd_per_year").onChange({
                target: { value: v, name: "fixed_costs_usd_per_year" },
              });
            }}
            min={0}
            step={100}
            suffix="USD/año"
            hint="Arriendos, salarios fijos, SaaS, etc."
            error={formState.errors.fixed_costs_usd_per_year?.message}
          />
          <input
            type="hidden"
            {...register("fixed_costs_usd_per_year", { valueAsNumber: true })}
          />
          <NumberField
            label="Costos variables"
            value={variable}
            onChange={(v) => {
              register("variable_costs_pct_of_revenue").onChange({
                target: {
                  value: v,
                  name: "variable_costs_pct_of_revenue",
                },
              });
            }}
            min={0}
            max={100}
            step={0.5}
            suffix="% del ingreso"
            hint="COGS, comisiones, fulfillment por unidad."
            error={formState.errors.variable_costs_pct_of_revenue?.message}
          />
          <input
            type="hidden"
            {...register("variable_costs_pct_of_revenue", {
              valueAsNumber: true,
            })}
          />
        </div>
      </Card>

      <Card
        title="Resumen de costos (calculado)"
        subtitle="Tomado de los pasos anteriores — proyección preliminar."
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card p-4 bg-navy-50/40">
            <div className="text-xs uppercase tracking-wider text-navy-500 font-medium">
              CAPEX total
            </div>
            <div className="mt-2 text-2xl font-semibold font-mono text-navy-900">
              ${totalCapex(state).toLocaleString()}
            </div>
            <p className="text-xs text-navy-500 mt-1">
              Suma de Recursos Clave.
            </p>
          </div>
          <div className="card p-4 bg-navy-50/40">
            <div className="text-xs uppercase tracking-wider text-navy-500 font-medium">
              OPEX anual
            </div>
            <div className="mt-2 text-2xl font-semibold font-mono text-navy-900">
              ${totalOpex(state).toLocaleString()}
            </div>
            <p className="text-xs text-navy-500 mt-1">
              Fijos + Actividades + Socios.
            </p>
          </div>
          <div className="card p-4 bg-navy-50/40">
            <div className="text-xs uppercase tracking-wider text-navy-500 font-medium">
              Variable
            </div>
            <div className="mt-2 text-2xl font-semibold font-mono text-navy-900">
              {variable}%
            </div>
            <p className="text-xs text-navy-500 mt-1">
              % del ingreso (COGS / comisiones).
            </p>
          </div>
        </div>
      </Card>

      <WizardFooter onBack={goBack} onNext={() => onSubmit()} />
    </form>
  );
}
