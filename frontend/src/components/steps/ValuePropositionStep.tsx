/**
 * Step 3 — Value Proposition.
 *
 * Lets the entrepreneur fill out the VPD block (products/services,
 * pain relievers, gain creators) and the headline + alternatives.
 *
 * Targets the segment names picked in step 2 — the smallest viable audience.
 */

import { Controller, useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { clsx } from "clsx";

import { Card, StepHeader, TextField, WizardFooter } from "../ui";
import { useWizard } from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";

const valuePropSchema = z.object({
  headline: z.string().min(5, "El headline debe tener al menos 5 caracteres"),
  description: z.string().default(""),
  products_services: z
    .array(z.object({ value: z.string().min(1, "Requerido") }))
    .min(1, "Define al menos un producto o servicio"),
  pain_relievers: z.array(z.object({ value: z.string().min(1) })),
  gain_creators: z.array(z.object({ value: z.string().min(1) })),
  target_segment_names: z.array(z.string()),
  alternatives: z.array(z.object({ value: z.string() })),
});

const formSchema = z.object({
  value_propositions: z.array(valuePropSchema).min(1),
});

type FormData = z.infer<typeof formSchema>;

export function ValuePropositionStep({ goNext, goBack }: StepProps) {
  const { state, dispatch } = useWizard();
  const segments = state.customer_segments;
  const segmentNames = segments.map((s) => s.name).filter(Boolean);

  const { control, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      value_propositions:
        state.value_propositions.length > 0
          ? (state.value_propositions.map((vp) => ({
              headline: vp.headline,
              description: vp.description,
              products_services: vp.products_services.map((value) => ({ value })),
              pain_relievers: vp.pain_relievers.map((value) => ({ value })),
              gain_creators: vp.gain_creators.map((value) => ({ value })),
              target_segment_names: vp.target_segment_names,
              alternatives: vp.alternatives.map((value) => ({ value })),
            })) as unknown as FormData["value_propositions"])
          : [
              {
                headline: "",
                description: "",
                products_services: [{ value: "" }],
                pain_relievers: [],
                gain_creators: [],
                target_segment_names: segmentNames.slice(0, 1),
                alternatives: [],
              },
            ],
    },
    mode: "onSubmit",
  });

  const vpArr = useFieldArray({ control, name: "value_propositions" });
  const errs = formState.errors.value_propositions?.[0];

  const onSubmit = handleSubmit((data) => {
    const vps = data.value_propositions.map((vp) => ({
      headline: vp.headline,
      description: vp.description,
      products_services: vp.products_services.map((p) => p.value),
      pain_relievers: vp.pain_relievers.map((p) => p.value),
      gain_creators: vp.gain_creators.map((p) => p.value),
      target_segment_names: vp.target_segment_names,
      alternatives: vp.alternatives.map((p) => p.value),
    }));
    dispatch({ type: "SET_VALUE_PROPOSITIONS", payload: vps });
    goNext();
  });

  return (
    <form onSubmit={onSubmit}>
      <StepHeader
        step={3}
        total={10}
        title="Propuesta de valor"
        subtitle="El encaje entre lo que tu cliente intenta lograr (jobs / pains / gains) y lo que tu producto hace al respecto (products / pain relievers / gain creators)."
      />

      {vpArr.fields.map((field, idx) => (
        <Card key={field.id} className="mb-6" title={`Propuesta de valor ${idx + 1}`}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Controller
              control={control}
              name={`value_propositions.${idx}.headline`}
              render={({ field }) => (
                <TextField
                  label="Headline (oración única)"
                  value={field.value ?? ""}
                  onChange={field.onChange}
                  onBlur={field.onBlur}
                  placeholder="Ej. Conectamos cafeterías specialty con caficultores de finca en 7 días."
                  error={errs?.headline?.message}
                />
              )}
            />
            <Controller
              control={control}
              name={`value_propositions.${idx}.description`}
              render={({ field }) => (
                <TextField
                  label="Descripción (1-2 frases)"
                  value={field.value ?? ""}
                  onChange={field.onChange}
                  onBlur={field.onBlur}
                  placeholder="Contexto y diferenciación."
                />
              )}
            />
          </div>

          <div>
            <label className="label">Segmentos objetivo</label>
            {segmentNames.length === 0 ? (
              <p className="text-sm text-navy-500 italic">
                Aún no definiste segmentos en el paso anterior. Vuelve y agrega al
                menos uno.
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {segmentNames.map((name) => (
                  <SegmentChip
                    key={name}
                    name={name}
                    control={control}
                    vpIndex={idx}
                  />
                ))}
              </div>
            )}
          </div>

          <StringListInput
            title="Productos / servicios"
            subtitle="Qué entregas concretamente"
            fieldName={`value_propositions.${idx}.products_services`}
            control={control}
            error={errs?.products_services?.message as string | undefined}
            placeholder="Ej. Plataforma SaaS de procurement de café verde"
          />
          <StringListInput
            title="Pain relievers"
            subtitle="Cómo alivia cada uno de los pains del segmento"
            fieldName={`value_propositions.${idx}.pain_relievers`}
            control={control}
            placeholder="Ej. Trazabilidad blockchain de finca a puerto"
          />
          <StringListInput
            title="Gain creators"
            subtitle="Cómo creas los outcomes que el cliente desea"
            fieldName={`value_propositions.${idx}.gain_creators`}
            control={control}
            placeholder="Ej. Catación virtual mensual con productores"
          />
          <StringListInput
            title="Alternativas / competencia"
            subtitle="Qué opciones tiene el cliente hoy si no te elige"
            fieldName={`value_propositions.${idx}.alternatives`}
            control={control}
            placeholder="Ej. Importadores tradicionales, plataformas globales"
          />
        </Card>
      ))}

      {vpArr.fields.length < 3 && (
        <div className="mb-6">
          <button
            type="button"
            onClick={() =>
              vpArr.append({
                headline: "",
                description: "",
                products_services: [{ value: "" }],
                pain_relievers: [],
                gain_creators: [],
                target_segment_names: [],
                alternatives: [],
              })
            }
            className="btn-secondary"
          >
            + Agregar propuesta de valor
          </button>
        </div>
      )}

      <WizardFooter onBack={goBack} onNext={() => onSubmit()} />
    </form>
  );
}

function SegmentChip({
  name,
  control,
  vpIndex,
}: {
  name: string;
  control: ReturnType<typeof useForm<FormData>>["control"];
  vpIndex: number;
}) {
  return (
    <Controller
      control={control}
      name={`value_propositions.${vpIndex}.target_segment_names`}
      render={({ field }) => {
        const selected = (field.value ?? []).includes(name);
        return (
          <button
            type="button"
            onClick={() => {
              const current = field.value ?? [];
              field.onChange(
                selected
                  ? current.filter((n) => n !== name)
                  : [...current, name],
              );
            }}
            className={clsx(
              "px-3 py-1.5 rounded-full text-sm font-medium border transition-colors",
              selected
                ? "bg-navy-900 text-white border-navy-900"
                : "bg-white text-navy-700 border-navy-200 hover:border-navy-400",
            )}
          >
            {name}
          </button>
        );
      }}
    />
  );
}

function StringListInput({
  title,
  subtitle,
  fieldName,
  control,
  error,
  placeholder,
}: {
  title: string;
  subtitle: string;
  fieldName: `value_propositions.${number}.${"products_services" | "pain_relievers" | "gain_creators" | "alternatives"}`;
  control: ReturnType<typeof useForm<FormData>>["control"];
  error?: string;
  placeholder?: string;
}) {
  const arr = useFieldArray({ control, name: fieldName });
  return (
    <div className="mt-6 pt-6 border-t border-navy-100">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-navy-700">
            {title}
          </h3>
          <p className="text-xs text-navy-500">{subtitle}</p>
        </div>
        <button
          type="button"
          onClick={() => arr.append({ value: "" })}
          className="text-xs px-3 py-1 rounded border border-navy-200 hover:bg-navy-50"
        >
          + Agregar
        </button>
      </div>
      <div className="space-y-2">
        {arr.fields.length === 0 && (
          <p className="text-xs text-navy-400 italic">Sin items.</p>
        )}
        {arr.fields.map((f, i) => (
          <div key={f.id} className="flex gap-2">
            <Controller
              control={control}
              name={`${fieldName}.${i}.value`}
              render={({ field }) => (
                <input
                  className="input flex-1"
                  placeholder={placeholder}
                  value={field.value ?? ""}
                  onChange={field.onChange}
                  onBlur={field.onBlur}
                />
              )}
            />
            <button
              type="button"
              onClick={() => arr.remove(i)}
              className="text-xs text-red-600 hover:underline px-2"
              aria-label="Quitar"
            >
              Quitar
            </button>
          </div>
        ))}
        {error && <p className="text-xs text-red-600">{error}</p>}
      </div>
    </div>
  );
}
