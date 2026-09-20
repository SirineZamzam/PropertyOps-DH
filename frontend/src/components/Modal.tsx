import { X } from "lucide-react";

import type {
  ReactNode,
} from "react";


export function Modal({
  title,
  eyebrow,
  onClose,
  children,
  wide = false,
}: {
  title: string;
  eyebrow?: string;
  onClose: () => void;
  children: ReactNode;
  wide?: boolean;
}) {
  return (
    <div className="fixed inset-0 z-[100] grid place-items-center bg-black/35 p-4 backdrop-blur-sm">
      <div
        className={[
          "max-h-[90vh] w-full overflow-y-auto rounded-[2rem] bg-white p-6 shadow-2xl dark:bg-dark-card",
          wide
            ? "max-w-5xl"
            : "max-w-lg",
        ].join(" ")}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            {eyebrow && (
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
                {eyebrow}
              </p>
            )}

            <h2 className="mt-1 text-2xl font-semibold tracking-[-0.04em] text-deep-blue dark:text-white">
              {title}
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="grid size-10 place-items-center rounded-xl bg-cyan/40 text-deep-blue dark:bg-moss dark:text-lime-soft"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-6">
          {children}
        </div>
      </div>
    </div>
  );
}


export const inputClass =
  "w-full rounded-2xl border border-celestial/15 bg-[#f7fafb] px-4 py-3 text-sm font-medium text-deep-blue outline-none transition placeholder:text-deep-blue/30 focus:border-celestial/55 focus:ring-4 focus:ring-cyan/15 dark:border-ash/12 dark:bg-phthalo dark:text-white dark:placeholder:text-white/30 dark:focus:border-ash/40";