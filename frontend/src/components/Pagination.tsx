import {
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import type {
  PageMeta,
} from "../types/domain";


export function Pagination({
  meta,
  onChange,
}: {
  meta: PageMeta;
  onChange: (
    page: number,
  ) => void;
}) {
  if (
    meta.total_pages <= 1
  ) {
    return null;
  }

  return (
    <div className="mt-8 flex flex-col gap-3 rounded-[1.4rem] border border-celestial/10 bg-white px-4 py-3 sm:flex-row sm:items-center sm:justify-between dark:border-ash/10 dark:bg-dark-card">
      <p className="text-xs text-deep-blue/45 dark:text-white/40">
        Page {meta.page} of{" "}
        {meta.total_pages}
        {" · "}
        {meta.total} records
      </p>

      <div className="flex gap-2">
        <button
          type="button"
          disabled={
            meta.page <= 1
          }
          onClick={() =>
            onChange(
              meta.page - 1,
            )
          }
          className="grid size-10 place-items-center rounded-xl bg-cyan text-deep-blue transition hover:bg-celestial hover:text-white disabled:opacity-30 dark:bg-moss dark:text-lime-soft"
        >
          <ChevronLeft
            size={17}
          />
        </button>

        <button
          type="button"
          disabled={
            meta.page >=
            meta.total_pages
          }
          onClick={() =>
            onChange(
              meta.page + 1,
            )
          }
          className="grid size-10 place-items-center rounded-xl bg-cyan text-deep-blue transition hover:bg-celestial hover:text-white disabled:opacity-30 dark:bg-moss dark:text-lime-soft"
        >
          <ChevronRight
            size={17}
          />
        </button>
      </div>
    </div>
  );
}