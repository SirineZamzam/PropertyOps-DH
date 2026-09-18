import {
  Building2,
  DoorOpen,
} from "lucide-react";

import {
  useTenantHome,
} from "../contexts/TenantHomeContext";


export function HomeSelector() {
  const {
    homes,
    selectedHome,
    selectHome,
  } = useTenantHome();

  if (
    homes.length <= 1
  ) {
    return null;
  }

  return (
    <div className="no-scrollbar flex gap-3 overflow-x-auto pb-2">
      {homes.map(
        (home) => {
          const active =
            home.lease_id ===
            selectedHome
              ?.lease_id;

          return (
            <button
              key={
                home.lease_id
              }
              type="button"
              onClick={() =>
                selectHome(
                  home.lease_id,
                )
              }
              className={[
                "min-w-[220px] rounded-[1.4rem] border p-4 text-left transition",
                active
                  ? "border-celestial bg-cyan text-deep-blue shadow-sm dark:border-ash dark:bg-moss dark:text-lime-soft"
                  : "border-celestial/10 bg-white text-deep-blue hover:border-celestial/30 dark:border-ash/10 dark:bg-dark-card dark:text-white",
              ].join(" ")}
            >
              <div className="flex items-center gap-3">
                <div
                  className={[
                    "grid size-10 place-items-center rounded-xl",
                    active
                      ? "bg-white/45"
                      : "bg-cyan/40 dark:bg-moss",
                  ].join(" ")}
                >
                  <Building2
                    size={18}
                  />
                </div>

                <div>
                  <p className="font-semibold">
                    {
                      home.property_name
                    }
                  </p>

                  <p className="mt-0.5 flex items-center gap-1 text-xs opacity-55">
                    <DoorOpen
                      size={12}
                    />

                    {
                      home.building_name
                    }{" "}
                    · Unit{" "}
                    {
                      home.unit_number
                    }
                  </p>
                </div>
              </div>
            </button>
          );
        },
      )}
    </div>
  );
}