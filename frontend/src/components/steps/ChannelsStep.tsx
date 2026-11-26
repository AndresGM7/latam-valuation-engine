/**
 * Step 4 — Channels.
 *
 * Add 1+ channels across the 5 phases (awareness / evaluation / purchase /
 * delivery / after-sales). cost_pct_of_revenue feeds the DCF.
 */

import { Controller, useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Card, NumberField, StepHeader, TextField, WizardFooter } from "../ui";
import { useWizard } from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";

const channelSchema = z.object({
  name: z.string().min(1, "Requerido"),
  channel_type: z.enum([
    "awareness",
    "evaluation",
    "purchase",
    "delivery",
    "after_sales",
  ]),
  description: z.string().default(""),
  cost_pct_of_revenue: z.coerce.number().min(0).max(100).default(0),
});

const formSchema = z.object({
  channels: z.array(channelSchema).min(1, "Mínimo 1 canal"),
});

type FormData = z.infer<typeof formSchema>;

const emptyChannel = {
  name: "",
  channel_type: "awareness" as const,
  description: "",
  cost_pct_of_revenue: 0,
};

const PHASES: Array<{ value: FormData["channels"][number]["channel_type"]; label: string }> = [
  { value: "awareness", label: "Awareness — cómo se enteran" },
  { value: "evaluation", label: "Evaluation — cómo evalúan tu propuesta" },
  { value: "purchase", label: "Purchase — cómo compran" },
  { value: "delivery", label: "Delivery — cómo les llega el producto" },
  { value: "after_sales", label: "After-sales — soporte post-venta" },
];

export function ChannelsStep({ goNext, goBack }: StepProps) {
  const { state, dispatch } = useWizard();

  const { control, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      channels:
        state.channels.length > 0
          ? (state.channels as unknown as FormData["channels"])
          : [emptyChannel],
    },
    mode: "onSubmit",
  });

  const arr = useFieldArray({ control, name: "channels" });
  const errors = formState.errors.channels;

  const onSubmit = handleSubmit((data) => {
    dispatch({ type: "SET_CHANNELS", payload: data.channels });
    goNext();
  });

  return (
    <form onSubmit={onSubmit}>
      <StepHeader
        step={4}
        total={10}
        title="Canales"
        subtitle="¿Cómo llega tu propuesta de valor al cliente? Cubre las 5 fases: awareness → evaluation → purchase → delivery → after-sales."
      />

      {arr.fields.map((field, idx) => {
        const err = errors?.[idx];
        return (
          <Card key={field.id} className="mb-4" title={`Canal ${idx + 1}`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Controller
                control={control}
                name={`channels.${idx}.name`}
                render={({ field: f }) => (
                  <TextField
                    label="Nombre del canal"
                    value={f.value ?? ""}
                    onChange={f.onChange}
                    onBlur={f.onBlur}
                    placeholder="Ej. Instagram orgánico"
                    error={err?.name?.message}
                  />
                )}
              />
              <div>
                <label className="label">Fase</label>
                <Controller
                  control={control}
                  name={`channels.${idx}.channel_type`}
                  render={({ field: f }) => (
                    <select
                      className="input"
                      value={f.value}
                      onChange={f.onChange}
                      onBlur={f.onBlur}
                    >
                      {PHASES.map((p) => (
                        <option key={p.value} value={p.value}>
                          {p.label}
                        </option>
                      ))}
                    </select>
                  )}
                />
              </div>
              <Controller
                control={control}
                name={`channels.${idx}.description`}
                render={({ field: f }) => (
                  <TextField
                    label="Descripción"
                    value={f.value ?? ""}
                    onChange={f.onChange}
                    onBlur={f.onBlur}
                    placeholder="Detalles operativos"
                  />
                )}
              />
              <Controller
                control={control}
                name={`channels.${idx}.cost_pct_of_revenue`}
                render={({ field: f }) => (
                  <NumberField
                    label="Costo como % del ingreso"
                    value={f.value ?? 0}
                    onChange={f.onChange}
                    min={0}
                    max={100}
                    step={0.5}
                    suffix="%"
                    hint="Para análisis de sensibilidad del DCF."
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
                  Quitar canal
                </button>
              )}
            </div>
          </Card>
        );
      })}

      <div className="mb-6">
        <button
          type="button"
          onClick={() => arr.append(emptyChannel)}
          className="btn-secondary"
        >
          + Agregar canal
        </button>
      </div>

      <WizardFooter onBack={goBack} onNext={() => onSubmit()} />
    </form>
  );
}
