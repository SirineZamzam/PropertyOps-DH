import type {
  ReactNode,
} from "react";


export function FormField({
  label,
  error,
  hint,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-bold text-deep-blue/65 dark:text-lime-soft/70">
        {label}
      </span>

      {children}

      {error ? (
        <p className="mt-1.5 text-xs font-medium text-red-600 dark:text-red-300">
          {error}
        </p>
      ) : hint ? (
        <p className="mt-1.5 text-xs text-deep-blue/40 dark:text-white/35">
          {hint}
        </p>
      ) : null}
    </label>
  );
}


export const controlClass =
  "w-full rounded-2xl border border-celestial/15 bg-white px-4 py-3 text-sm font-medium text-deep-blue outline-none transition placeholder:text-deep-blue/30 focus:border-celestial/60 focus:ring-4 focus:ring-cyan/20 disabled:cursor-not-allowed disabled:opacity-45 dark:border-ash/15 dark:bg-phthalo dark:text-white dark:placeholder:text-white/30 dark:focus:border-ash/45 dark:focus:ring-moss/40";