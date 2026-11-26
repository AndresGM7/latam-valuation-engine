/**
 * Step 2 — Customer Segments.
 *
 * Lets the entrepreneur add up to 3 customer segments with the full
 * VPD customer profile (jobs / pains / gains) inside each segment.
 * Mirrors the dataclasses:
 *   CustomerSegment { name, description, segment_type, profile: { jobs, pains, gains } }
 */

import { Controller, useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { clsx } from "clsx";

import {
  Card,
  NumberField,
  StepHeader,
  TextAreaField,
  TextField,
  WizardFooter,
} from "../ui";
import { useWizard } from "../../lib/wizardStore";
import type { StepProps } from "./WelcomeStep";

const segmentSchema = z.object({
  name: z.string().min(1, "Nombre requerido"),
  description: z.string().default(""),
  segment_type: z.enum([
    "mass_market",
    "niche",
    "segmented",
    "diversified",
    "multi_sided",
  ]),
  jobs: z.array(
    z.object({
      description: z.string().min(1, "Descripción requerida"),
      job_type: z.enum(["functional", "social", "emotional"]),
      importance: z.coerce.number().min(0).max(5),
      satisfaction: z.coerce.number().min(0).max(5),
    }),
  ),
  pains: z.array(
    z.object({
      description: z.string().min(1, "Descripción requerida"),
      severity: z.coerce.number().min(0).max(5),
      frequency: z.coerce.number().min(0).max(5),
    }),
  ),
  gains: z.array(
    z.object({
      description: z.string().min(1, "Descripción requerida"),
      relevance: z.coerce.number().min(0).max(5),
      gain_type: z.enum(["required", "expected", "desired", "unexpected"]),
    }),
  ),
});

const formSchema = z.object({
  segments: z.array(segmentSchema).min(1, "Mínimo 1 segmento").max(3),
});

type FormData = z.infer<typeof formSchema>;

const emptyJob = { description: "", job_type: "functional" as const, importance: 3, satisfaction: 3 };
const emptyPain = { description: "", severity: 3, frequency: 3 };
const emptyGain = { description: "", relevance: 3, gain_type: "expected" as const };

export function CustomerSegmentsStep({ goNext, goBack }: StepProps) {
  const { state, dispatch } = useWizard();

  const { control, handleSubmit, formState, watch } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      segments:
        state.customer_segments.length > 0
          ? (state.customer_segments as unknown as FormData["segments"])
          : [
              {
                name: "",
                description: "",
                segment_type: "niche" as const,
                jobs: [],
                pains: [],
                gains: [],
              },
            ],
    },
    mode: "onSubmit",
  });

  const segmentArr = useFieldArray({ control, name: "segments" });
  const segCount = watch("segments").length;

  const onSubmit = handleSubmit((data) => {
    dispatch({ type: "SET_CUSTOMER_SEGMENTS", payload: data.segments });
    goNext();
  });

  return (
    <form onSubmit={onSubmit}>
      <StepHeader
        step={2}
        total={10}
        title="Segmentos de cliente"
        subtitle="Hasta 3 segmentos (Seth Godin: smallest viable audience). Para cada uno, identifica los trabajos que intentan hacer, sus pains y sus gains."
      />

      {segmentArr.fields.map((field, sIdx) => (
        <SegmentCard
          key={field.id}
          index={sIdx}
          control={control}
          formState={formState}
          onRemove={() => segmentArr.remove(sIdx)}
          canRemove={segCount > 1}
        />
      ))}

      {segCount < 3 && (
        <div className="mb-6">
          <button
            type="button"
            onClick={() =>
              segmentArr.append({
                name: "",
                description: "",
                segment_type: "niche",
                jobs: [],
                pains: [],
                gains: [],
              })
            }
            className="btn-secondary"
          >
            + Agregar segmento ({segCount}/3)
          </button>
        </div>
      )}

      {formState.errors.segments?.root && (
        <p className="text-sm text-red-600">
          {formState.errors.segments.root.message}
        </p>
      )}

      <WizardFooter onBack={goBack} onNext={() => onSubmit()} />
    </form>
  );
}

function SegmentCard({
  index,
  control,
  formState,
  onRemove,
  canRemove,
}: {
  index: number;
  control: ReturnType<typeof useForm<FormData>>["control"];
  formState: ReturnType<typeof useForm<FormData>>["formState"];
  onRemove: () => void;
  canRemove: boolean;
}) {
  const jobs = useFieldArray({ control, name: `segments.${index}.jobs` });
  const pains = useFieldArray({ control, name: `segments.${index}.pains` });
  const gains = useFieldArray({ control, name: `segments.${index}.gains` });

  const errs = formState.errors.segments?.[index];

  return (
    <Card
      className="mb-6"
      title={`Segmento ${index + 1}`}
      action={
        canRemove ? (
          <button
            type="button"
            onClick={onRemove}
            className="text-xs text-red-600 hover:underline"
          >
            Eliminar
          </button>
        ) : undefined
      }
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Controller
          control={control}
          name={`segments.${index}.name`}
          render={({ field }) => (
            <TextField
              label="Nombre del segmento"
              value={field.value ?? ""}
              onChange={field.onChange}
              onBlur={field.onBlur}
              placeholder="Ej. Dueños de cafeterías specialty en Bogotá"
              error={errs?.name?.message}
            />
          )}
        />
        <div className="md:col-span-2">
          <Controller
            control={control}
            name={`segments.${index}.description`}
            render={({ field }) => (
              <TextAreaField
                label="Descripción"
                value={field.value ?? ""}
                onChange={field.onChange}
                onBlur={field.onBlur}
                placeholder="Geografía, demografía, comportamiento de compra, etc."
                rows={2}
              />
            )}
          />
        </div>
        <div>
          <label className="label">Tipo de segmento</label>
          <Controller
            control={control}
            name={`segments.${index}.segment_type`}
            render={({ field }) => (
              <select
                className="input"
                value={field.value}
                onChange={field.onChange}
                onBlur={field.onBlur}
              >
                <option value="mass_market">Mass market</option>
                <option value="niche">Nicho</option>
                <option value="segmented">Segmentado</option>
                <option value="diversified">Diversificado</option>
                <option value="multi_sided">Multi-sided</option>
              </select>
            )}
          />
        </div>
      </div>

      {/* JOBS */}
      <SubBlock
        title="Customer Jobs"
        subtitle="¿Qué intentan lograr? (functional / social / emotional)"
        items={jobs.fields}
        onAdd={() => jobs.append(emptyJob)}
        renderItem={(_j, jIdx) => {
          const jobErr = errs?.jobs?.[jIdx];
          return (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-start">
              <div className="md:col-span-6">
                <Controller
                  control={control}
                  name={`segments.${index}.jobs.${jIdx}.description`}
                  render={({ field }) => (
                    <input
                      className={clsx(
                        "input",
                        jobErr?.description && "border-red-500",
                      )}
                      placeholder="Ej. Comprar café verde de origen"
                      value={field.value ?? ""}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                    />
                  )}
                />
                {jobErr?.description && (
                  <p className="mt-1 text-xs text-red-600">
                    {jobErr.description.message}
                  </p>
                )}
              </div>
              <div className="md:col-span-2">
                <Controller
                  control={control}
                  name={`segments.${index}.jobs.${jIdx}.job_type`}
                  render={({ field }) => (
                    <select
                      className="input"
                      value={field.value}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                    >
                      <option value="functional">Functional</option>
                      <option value="social">Social</option>
                      <option value="emotional">Emotional</option>
                    </select>
                  )}
                />
              </div>
              <Controller
                control={control}
                name={`segments.${index}.jobs.${jIdx}.importance`}
                render={({ field }) => (
                  <NumberField
                    label="Importance"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    max={5}
                  />
                )}
              />
              <Controller
                control={control}
                name={`segments.${index}.jobs.${jIdx}.satisfaction`}
                render={({ field }) => (
                  <NumberField
                    label="Satisfaction"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    max={5}
                  />
                )}
              />
              <div className="md:col-span-2 flex items-end">
                <button
                  type="button"
                  onClick={() => jobs.remove(jIdx)}
                  className="text-xs text-red-600 hover:underline pb-2"
                  aria-label="Eliminar job"
                >
                  Quitar
                </button>
              </div>
            </div>
          );
        }}
      />

      {/* PAINS */}
      <SubBlock
        title="Pains"
        subtitle="Frustraciones, obstáculos, riesgos (severity x frequency)"
        items={pains.fields}
        onAdd={() => pains.append(emptyPain)}
        renderItem={(_p, pIdx) => {
          const painErr = errs?.pains?.[pIdx];
          return (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-start">
              <div className="md:col-span-7">
                <Controller
                  control={control}
                  name={`segments.${index}.pains.${pIdx}.description`}
                  render={({ field }) => (
                    <input
                      className={clsx(
                        "input",
                        painErr?.description && "border-red-500",
                      )}
                      placeholder="Ej. Largos tiempos de entrega del importador"
                      value={field.value ?? ""}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                    />
                  )}
                />
                {painErr?.description && (
                  <p className="mt-1 text-xs text-red-600">
                    {painErr.description.message}
                  </p>
                )}
              </div>
              <Controller
                control={control}
                name={`segments.${index}.pains.${pIdx}.severity`}
                render={({ field }) => (
                  <NumberField
                    label="Severity"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    max={5}
                  />
                )}
              />
              <Controller
                control={control}
                name={`segments.${index}.pains.${pIdx}.frequency`}
                render={({ field }) => (
                  <NumberField
                    label="Frequency"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    max={5}
                  />
                )}
              />
              <div className="md:col-span-1 flex items-end">
                <button
                  type="button"
                  onClick={() => pains.remove(pIdx)}
                  className="text-xs text-red-600 hover:underline pb-2"
                >
                  Quitar
                </button>
              </div>
            </div>
          );
        }}
      />

      {/* GAINS */}
      <SubBlock
        title="Gains"
        subtitle="Beneficios / outcomes que el cliente desea"
        items={gains.fields}
        onAdd={() => gains.append(emptyGain)}
        renderItem={(_g, gIdx) => {
          const gainErr = errs?.gains?.[gIdx];
          return (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-start">
              <div className="md:col-span-7">
                <Controller
                  control={control}
                  name={`segments.${index}.gains.${gIdx}.description`}
                  render={({ field }) => (
                    <input
                      className={clsx(
                        "input",
                        gainErr?.description && "border-red-500",
                      )}
                      placeholder="Ej. Trazabilidad de finca a taza"
                      value={field.value ?? ""}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                    />
                  )}
                />
                {gainErr?.description && (
                  <p className="mt-1 text-xs text-red-600">
                    {gainErr.description.message}
                  </p>
                )}
              </div>
              <Controller
                control={control}
                name={`segments.${index}.gains.${gIdx}.relevance`}
                render={({ field }) => (
                  <NumberField
                    label="Relevance"
                    value={field.value ?? 0}
                    onChange={field.onChange}
                    min={0}
                    max={5}
                  />
                )}
              />
              <div className="md:col-span-2">
                <Controller
                  control={control}
                  name={`segments.${index}.gains.${gIdx}.gain_type`}
                  render={({ field }) => (
                    <select
                      className="input"
                      value={field.value}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                    >
                      <option value="required">Required</option>
                      <option value="expected">Expected</option>
                      <option value="desired">Desired</option>
                      <option value="unexpected">Unexpected</option>
                    </select>
                  )}
                />
              </div>
              <div className="md:col-span-1 flex items-end">
                <button
                  type="button"
                  onClick={() => gains.remove(gIdx)}
                  className="text-xs text-red-600 hover:underline pb-2"
                >
                  Quitar
                </button>
              </div>
            </div>
          );
        }}
      />
    </Card>
  );
}

function SubBlock<T>({
  title,
  subtitle,
  items,
  onAdd,
  renderItem,
}: {
  title: string;
  subtitle: string;
  items: T[];
  onAdd: () => void;
  renderItem: (item: T, idx: number) => React.ReactNode;
}) {
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
          onClick={onAdd}
          className="text-xs px-3 py-1 rounded border border-navy-200 hover:bg-navy-50"
        >
          + Agregar
        </button>
      </div>
      <div className="space-y-3">
        {items.length === 0 && (
          <p className="text-xs text-navy-400 italic">
            Aún no has agregado ninguno. Clic en "+ Agregar".
          </p>
        )}
        {items.map((item, idx) => (
          <div key={idx}>{renderItem(item, idx)}</div>
        ))}
      </div>
    </div>
  );
}
