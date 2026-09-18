import { Building2 } from "lucide-react";


interface BrandProps {
  light?: boolean;
  compact?: boolean;
}


export function Brand({
  light = false,
  compact = false,
}: BrandProps) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={[
          "grid size-10 shrink-0 place-items-center rounded-2xl",
          light
            ? "bg-white/14 text-white"
            : "bg-phthalo text-white",
        ].join(" ")}
      >
        <Building2 size={20} />
      </div>

      {!compact && (
        <div>
          <div
            className={[
              "text-lg font-bold tracking-[-0.04em]",
              light
                ? "text-white"
                : "text-phthalo",
            ].join(" ")}
          >
            PropertyOps
          </div>

          <div
            className={[
              "text-[10px] font-semibold uppercase tracking-[0.18em]",
              light
                ? "text-white/60"
                : "text-moss/65",
            ].join(" ")}
          >
            Property Operations
          </div>
        </div>
      )}
    </div>
  );
}