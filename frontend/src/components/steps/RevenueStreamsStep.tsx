/**
 * Step 5 — Revenue Streams.
 *
 * Each stream has ARPU, year-1 volume and a growth rate.
 * These are the inputs to the DCF (see BusinessModel.to_financial_inputs).
 */

import { Controller, useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Card, NumberField, StepHeader, TextField, WizardFooter } from "../ui";
import { useWizard } from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";

const streamSchema = z.object({
  name: z.string().min(1, "Requerido"),
  stream_type: z.enum([
    "one_time_sale",
    "subscription",
    "usage_fee",
    "lending",
    "licensing",
    "advertising",
    "marketplace_commission",
    "leasing",
  ]),
  pricing_mechanism: z.string().default(""),
  estimated_arpu_usd_per_year: z.coerce.number().min(0).default(0),
  estimated_volume_year_1: z.coerce.number().min(0).int().default(0),
  growth_rate_pct_year: z.coerce.number().min(-50).max(500).default(0),
});

const formSchema = z.object({
  streams: z.array(streamSchema).min(1, "Mínimo 1 fuente de ingreso"),
});

type FormData = z.infer<typeof formSchema>;

const emptyStream = {
  name: "",
  stream_type: "subscription" as const,
  pricing_mechanism: "",
  estimated_arpu_usd_per_year: 0,
  estimated_volume_year_1: 0,
  growth_rate_pct_year: 0,
};

export function RevenueStreamsStep({ goNext, goBack }: StepProps) {
  const { state, dispatch } = useWizard();

  const { control, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      streams:
        state.revenue_streams.length > 0
          ? (state.revenue_streams as unknown as FormData["streams"])
          : [emptyStream],
    },
    mode: "onSubmit",
  });

  const arr = useFieldArray({ control, name: "streams" });
  const errors = formState.errors.streams;

  const onSubmit = handleSubmit((data) => {
    dispatch({ type: "SET_REVENUE_STREAMS", payload: data.streams });
    goNext();
  });

  return (
    <form onSubmit={onSubmit}>
      <StepHeader
        step={5}
        total={10}
        title="Fuentes de ingreso"
        subtitle="Cada stream: precio anual (ARPU), volumen año 1 y crecimiento esperado. Estos números alimentan directamente el DCF."
      />

      {arr.fields.map((field, idx) => {
        const err = errors?.[idx];
        const stream = field;
        return (
          <Card key={stream.id} className="mb-4" title={`Stream ${idx + 1}`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Controller
                control={control}
                name={`streams.${idx}.name`}
                render={({ field: f }) => (
                  <TextField
                    label="Nombre"
                    value={f.value ?? ""}
                    onChange={f.onChange}
                    onBlur={f.onBlur}
                    placeholder="Ej. Suscripción mensual Pro"
                    error={err?.name?.message}
                  />
                )}
              />
              <div>
                <label className="label">Tipo</label>
                <Controller
                  control={control}
                  name={`streams.${idx}.stream_type`}
                  render={({ field: f }) => (
                    <select
                      className="input"
                      value={f.value}
                      onChange={f.onChange}
                      onBlur={f.onBlur}
                    >
                      <option value="one_time_sale">Venta única</option>
                      <option value="subscription">Suscripción</option>
                      <option value="usage_fee">Uso / consumo</option>
                      <option value="lending">Préstamo</option>
                      <option value="licensing">Licencia</option>
                      <option value="advertising">Publicidad</option>
                      <option value="marketplace_commission">
                        Comisión marketplace
                      </option>
                      <option value="leasing">Leasing</option>
                    </select>
                  )}
                />
              </div>
              <Controller
                control={control}
                name={`streams.${idx}.pricing_mechanism`}
                render={({ field: f }) => (
                  <TextField
                    label="Mecanismo de pricing"
                    value={f.value ?? ""}
                    onChange={f.onChange}
                    onBlur={f.onBlur}
                    placeholder="Ej. USD 49/mes por usuario, 5% GMV, etc."
                  />
                )}
              />
              <Controller
                control={control}
                name={`streams.${idx}.estimated_arpu_usd_per_year`}
                render={({ field: f }) => (
                  <NumberField
                    label="ARPU"
                    value={f.value ?? 0}
                    onChange={f.onChange}
                    min={0}
                    step={1}
                    suffix="USD/año"
                  />
                )}
              />
              <Controller
                control={control}
                name={`streams.${idx}.estimated_volume_year_1`}
                render={({ field: f }) => (
                  <NumberField
                    label="Volumen año 1"
                    value={f.value ?? 0}
                    onChange={f.onChange}
                    min={0}
                    step={1}
                    hint="Clientes / transacciones / contratos"
                  />
                )}
              />
              <Controller
                control={control}
                name={`streams.${idx}.growth_rate_pct_year`}
                render={({ field: f }) => (
                  <NumberField
                    label="Crecimiento anual"
                    value={f.value ?? 0}
                    onChange={f.onChange}
                    min={-50}
                    max={500}
                    step={1}
                    suffix="%"
                  />
                )}
              />
            </div>
            <div className="mt-3 text-right">
              {arr.fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => arr.remove(idx)}
                  className="text-xs text-red-600 hover:underline"
                >
                  Quitar stream
                </button>
              )}
            </div>
          </Card>
        );
      })}

      <div className="mb-6">
        <button
          type="button"
          onClick={() => arr.append(emptyStream)}
          className="btn-secondary"
        >
          + Agregar fuente de ingreso
        </button>
      </div>

      <WizardFooter onBack={goBack} onNext={() => onSubmit()} />
    </form>
  );
}
