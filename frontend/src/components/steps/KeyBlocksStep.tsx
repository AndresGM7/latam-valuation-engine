/**
 * Step 6 — Key Resources + Activities + Partners (the three blocks of
 * the BMC that drive the cost side of the DCF).
 */

import { Controller, useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Card, NumberField, StepHeader, TextField, WizardFooter } from "../ui";
import { useWizard } from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";

const resourceSchema = z.object({
  name: z.string().min(1, "Requerido"),
  resource_type: z.string().default("physical"),
  description: z.string().default(""),
  estimated_capex_usd: z.coerce.number().min(0).default(0),
});
const activitySchema = z.object({
  name: z.string().min(1, "Requerido"),
  description: z.string().default(""),
  estimated_opex_usd_per_year: z.coerce.number().min(0).default(0),
});
const partnerSchema = z.object({
  name: z.string().min(1, "Requerido"),
  partner_type: z.string().default("supplier"),
  description: z.string().default(""),
  estimated_cost_usd_per_year: z.coerce.number().min(0).default(0),
});

const formSchema = z.object({
  resources: z.array(resourceSchema),
  activities: z.array(activitySchema),
  partners: z.array(partnerSchema),
});

type FormData = z.infer<typeof formSchema>;

const emptyResource = { name: "", resource_type: "physical", description: "", estimated_capex_usd: 0 };
const emptyActivity = { name: "", description: "", estimated_opex_usd_per_year: 0 };
const emptyPartner = { name: "", partner_type: "supplier", description: "", estimated_cost_usd_per_year: 0 };

export function KeyBlocksStep({ goNext, goBack }: StepProps) {
  const { state, dispatch } = useWizard();

  const { control, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      resources:
        state.key_resources.length > 0
          ? (state.key_resources as unknown as FormData["resources"])
          : [],
      activities:
        state.key_activities.length > 0
          ? (state.key_activities as unknown as FormData["activities"])
          : [],
      partners:
        state.key_partners.length > 0
          ? (state.key_partners as unknown as FormData["partners"])
          : [],
    },
    mode: "onSubmit",
  });

  const resources = useFieldArray({ control, name: "resources" });
  const activities = useFieldArray({ control, name: "activities" });
  const partners = useFieldArray({ control, name: "partners" });

  const errors = formState.errors;

  const onSubmit = handleSubmit((data) => {
    dispatch({ type: "SET_KEY_RESOURCES", payload: data.resources });
    dispatch({ type: "SET_KEY_ACTIVITIES", payload: data.activities });
    dispatch({ type: "SET_KEY_PARTNERS", payload: data.partners });
    goNext();
  });

  return (
    <form onSubmit={onSubmit}>
      <StepHeader
        step={6}
        total={10}
        title="Recursos, actividades y socios clave"
        subtitle="Los 3 bloques del lado del producto en el BMC. Los costos aquí son los opex/capex que alimentan el DCF."
      />

      {/* KEY RESOURCES */}
      <Card
        className="mb-6"
        title="Recursos clave"
        subtitle="Activos indispensables: físicos, intelectuales, humanos, financieros."
      >
        {resources.fields.length === 0 && (
          <p className="text-sm text-navy-500 italic mb-3">
            Ejemplos: equipo fundador, patentes, infraestructura cloud, inventario inicial.
          </p>
        )}
        {resources.fields.map((f, idx) => {
          const err = errors.resources?.[idx];
          return (
            <div key={f.id} className="grid grid-cols-1 md:grid-cols-12 gap-3 mb-3 pb-3 border-b border-navy-100 last:border-0">
              <Controller
                control={control}
                name={`resources.${idx}.name`}
                render={({ field }) => (
                  <TextField
                    label="Nombre"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Ej. Plataforma SaaS"
                    error={err?.name?.message}
                  />
                )}
              />
              <Controller
                control={control}
                name={`resources.${idx}.resource_type`}
                render={({ field }) => (
                  <TextField
                    label="Tipo"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="physical / intellectual / human / financial"
                  />
                )}
              />
              <Controller
                control={control}
                name={`resources.${idx}.description`}
                render={({ field }) => (
                  <TextField
                    label="Descripción"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Detalles"
                  />
                )}
              />
              <Controller
                control={control}
                name={`resources.${idx}.estimated_capex_usd`}
                render={({ field }) => (
                  <NumberField
                    label="CAPEX"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    step={100}
                    suffix="USD"
                    hint="Inversión inicial"
                  />
                )}
              />
              <div className="md:col-span-12 flex justify-end">
                <button
                  type="button"
                  onClick={() => resources.remove(idx)}
                  className="text-xs text-red-600 hover:underline"
                >
                  Quitar
                </button>
              </div>
            </div>
          );
        })}
        <button
          type="button"
          onClick={() => resources.append(emptyResource)}
          className="text-xs px-3 py-1 rounded border border-navy-200 hover:bg-navy-50"
        >
          + Agregar recurso
        </button>
      </Card>

      {/* KEY ACTIVITIES */}
      <Card
        className="mb-6"
        title="Actividades clave"
        subtitle="Lo que la empresa hace todos los días para entregar la PV."
      >
        {activities.fields.length === 0 && (
          <p className="text-sm text-navy-500 italic mb-3">
            Ejemplos: desarrollo de producto, marketing de contenidos, fulfillment.
          </p>
        )}
        {activities.fields.map((f, idx) => {
          const err = errors.activities?.[idx];
          return (
            <div key={f.id} className="grid grid-cols-1 md:grid-cols-12 gap-3 mb-3 pb-3 border-b border-navy-100 last:border-0">
              <Controller
                control={control}
                name={`activities.${idx}.name`}
                render={({ field }) => (
                  <TextField
                    label="Nombre"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Ej. Desarrollo de producto"
                    error={err?.name?.message}
                  />
                )}
              />
              <Controller
                control={control}
                name={`activities.${idx}.description`}
                render={({ field }) => (
                  <TextField
                    label="Descripción"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Detalles"
                  />
                )}
              />
              <Controller
                control={control}
                name={`activities.${idx}.estimated_opex_usd_per_year`}
                render={({ field }) => (
                  <NumberField
                    label="OPEX anual"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    step={100}
                    suffix="USD/año"
                  />
                )}
              />
              <div className="md:col-span-12 flex justify-end">
                <button
                  type="button"
                  onClick={() => activities.remove(idx)}
                  className="text-xs text-red-600 hover:underline"
                >
                  Quitar
                </button>
              </div>
            </div>
          );
        })}
        <button
          type="button"
          onClick={() => activities.append(emptyActivity)}
          className="text-xs px-3 py-1 rounded border border-navy-200 hover:bg-navy-50"
        >
          + Agregar actividad
        </button>
      </Card>

      {/* KEY PARTNERS */}
      <Card
        className="mb-6"
        title="Socios / aliados clave"
        subtitle="Proveedores, distribuidores, JV, etc."
      >
        {partners.fields.length === 0 && (
          <p className="text-sm text-navy-500 italic mb-3">
            Ejemplos: proveedor de logística, agencia de marketing, aliado estratégico.
          </p>
        )}
        {partners.fields.map((f, idx) => {
          const err = errors.partners?.[idx];
          return (
            <div key={f.id} className="grid grid-cols-1 md:grid-cols-12 gap-3 mb-3 pb-3 border-b border-navy-100 last:border-0">
              <Controller
                control={control}
                name={`partners.${idx}.name`}
                render={({ field }) => (
                  <TextField
                    label="Nombre"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Ej. Coordinadora Mercantil"
                    error={err?.name?.message}
                  />
                )}
              />
              <Controller
                control={control}
                name={`partners.${idx}.partner_type`}
                render={({ field }) => (
                  <TextField
                    label="Tipo"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="supplier / distributor / joint_venture"
                  />
                )}
              />
              <Controller
                control={control}
                name={`partners.${idx}.description`}
                render={({ field }) => (
                  <TextField
                    label="Descripción"
                    value={field.value ?? ""}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Detalles"
                  />
                )}
              />
              <Controller
                control={control}
                name={`partners.${idx}.estimated_cost_usd_per_year`}
                render={({ field }) => (
                  <NumberField
                    label="Costo anual"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    step={100}
                    suffix="USD/año"
                  />
                )}
              />
              <div className="md:col-span-12 flex justify-end">
                <button
                  type="button"
                  onClick={() => partners.remove(idx)}
                  className="text-xs text-red-600 hover:underline"
                >
                  Quitar
                </button>
              </div>
            </div>
          );
        })}
        <button
          type="button"
          onClick={() => partners.append(emptyPartner)}
          className="text-xs px-3 py-1 rounded border border-navy-200 hover:bg-navy-50"
        >
          + Agregar socio
        </button>
      </Card>

      <WizardFooter onBack={goBack} onNext={() => onSubmit()} />
    </form>
  );
}
