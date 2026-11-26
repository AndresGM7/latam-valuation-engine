/**
 * Lightweight reusable UI primitives — kept in one file so the wizard
 * screens read like documents rather than CSS-zoo.
 */

import { clsx } from "clsx";
import type { ReactNode } from "react";

export function ProgressBar({
  value,
  max = 100,
  label,
  tone = "navy",
  className,
}: {
  value: number;
  max?: number;
  label?: string;
  tone?: "navy" | "accent" | "amber" | "red";
  className?: string;
}) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const fill =
    tone === "accent"
      ? "bg-accent-500"
      : tone === "amber"
        ? "bg-amber-500"
        : tone === "red"
          ? "bg-red-500"
          : "bg-navy-700";
  return (
    <div className={clsx("w-full", className)}>
      {label && (
        <div className="flex justify-between items-center text-xs text-navy-600 mb-1">
          <span>{label}</span>
          <span className="font-mono">{pct.toFixed(0)}%</span>
        </div>
      )}
      <div className="w-full bg-navy-100 rounded-full h-2 overflow-hidden">
        <div
          className={clsx("h-full transition-all duration-500", fill)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function StepHeader({
  step,
  total,
  title,
  subtitle,
}: {
  step: number;
  total: number;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="mb-8">
      <div className="text-xs font-mono uppercase tracking-wider text-navy-500 mb-2">
        Paso {step} de {total}
      </div>
      <h1 className="section-title">{title}</h1>
      {subtitle && <p className="section-subtitle max-w-2xl">{subtitle}</p>}
    </div>
  );
}

export function WizardFooter({
  onBack,
  onNext,
  nextLabel = "Siguiente",
  backLabel = "Atrás",
  nextDisabled = false,
}: {
  onBack?: () => void;
  onNext?: () => void;
  nextLabel?: string;
  backLabel?: string;
  nextDisabled?: boolean;
}) {
  return (
    <div className="mt-10 pt-6 border-t border-navy-100 flex items-center justify-between">
      <div>
        {onBack && (
          <button type="button" onClick={onBack} className="btn-ghost">
            {backLabel}
          </button>
        )}
      </div>
      <div>
        {onNext && (
          <button
            type="button"
            onClick={onNext}
            className="btn-primary"
            disabled={nextDisabled}
          >
            {nextLabel}
          </button>
        )}
      </div>
    </div>
  );
}

export function Card({
  title,
  subtitle,
  children,
  className,
  action,
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}) {
  return (
    <section className={clsx("card p-6", className)}>
      {(title || action) && (
        <header className="flex items-start justify-between mb-4">
          <div>
            {title && (
              <h2 className="text-lg font-semibold text-navy-900">{title}</h2>
            )}
            {subtitle && (
              <p className="text-sm text-navy-500 mt-1">{subtitle}</p>
            )}
          </div>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

export function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="mt-1 text-xs text-red-600">{message}</p>;
}

export function StatTile({
  label,
  value,
  hint,
  tone = "navy",
}: {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "navy" | "accent";
}) {
  const valueColor = tone === "accent" ? "text-accent-700" : "text-navy-900";
  return (
    <div className="card p-4">
      <div className="text-xs uppercase tracking-wider text-navy-500 font-medium">
        {label}
      </div>
      <div className={clsx("mt-2 text-2xl font-semibold font-mono", valueColor)}>
        {value}
      </div>
      {hint && <div className="text-xs text-navy-500 mt-1">{hint}</div>}
    </div>
  );
}

export function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  hint,
  suffix,
  error,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  hint?: string;
  suffix?: string;
  error?: string;
}) {
  return (
    <div>
      <label className="label">{label}</label>
      <div className="relative">
        <input
          type="number"
          value={Number.isFinite(value) ? value : 0}
          min={min}
          max={max}
          step={step}
          onChange={(e) => {
            const v = parseFloat(e.target.value);
            onChange(Number.isNaN(v) ? 0 : v);
          }}
          className={clsx("input pr-12", error && "border-red-500")}
        />
        {suffix && (
          <span className="absolute inset-y-0 right-3 flex items-center text-xs text-navy-400 pointer-events-none">
            {suffix}
          </span>
        )}
      </div>
      {hint && <p className="mt-1 text-xs text-navy-500">{hint}</p>}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}

export function TextField({
  label,
  value,
  onChange,
  onBlur,
  placeholder,
  hint,
  error,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  hint?: string;
  error?: string;
}) {
  return (
    <div>
      <label className="label">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        placeholder={placeholder}
        className={clsx("input", error && "border-red-500")}
      />
      {hint && <p className="mt-1 text-xs text-navy-500">{hint}</p>}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}

export function TextAreaField({
  label,
  value,
  onChange,
  onBlur,
  placeholder,
  rows = 3,
  hint,
  error,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  rows?: number;
  hint?: string;
  error?: string;
}) {
  return (
    <div>
      <label className="label">{label}</label>
      <textarea
        value={value}
        rows={rows}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        placeholder={placeholder}
        className={clsx("textarea", error && "border-red-500")}
      />
      {hint && <p className="mt-1 text-xs text-navy-500">{hint}</p>}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
