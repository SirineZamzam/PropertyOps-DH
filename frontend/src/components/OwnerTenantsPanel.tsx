import {
  FilterX,
  Mail,
  MapPin,
  Phone,
  Search,
  UserRound,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  FormField,
  controlClass,
} from "./FormField";

import {
  LocationFields,
} from "./LocationFields";

import {
  Pagination,
} from "./Pagination";

import {
  apiRequest,
} from "../lib/api";

import type {
  OwnerTenantPage,
  PropertyNode,
} from "../types/domain";


const EMPTY_META = {
  page: 1,
  page_size: 8,
  total: 0,
  total_pages: 0,
};


export function OwnerTenantsPanel({
  structure,
}: {
  structure: PropertyNode[];
}) {
  const [data, setData] =
    useState<OwnerTenantPage>({
      items: [],
      meta: EMPTY_META,
    });

  const [page, setPage] =
    useState(1);

  const [propertyId, setPropertyId] =
    useState("");

  const [buildingId, setBuildingId] =
    useState("");

  const [unitId, setUnitId] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function load() {
    const params =
      new URLSearchParams({
        page: String(page),
        page_size: "8",
      });

    if (propertyId) {
      params.set(
        "property_id",
        propertyId,
      );
    }

    if (buildingId) {
      params.set(
        "building_id",
        buildingId,
      );
    }

    if (unitId) {
      params.set(
        "unit_id",
        unitId,
      );
    }

    if (search.trim()) {
      params.set(
        "tenant",
        search.trim(),
      );
    }

    setLoading(true);
    setError("");

    try {
      const response =
        await apiRequest<
          OwnerTenantPage
        >(
          `/owner/tenants/current?${params}`,
        );

      setData(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load tenants.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    const timer =
      window.setTimeout(
        () => {
          void load();
        },
        search.trim()
          ? 300
          : 0,
      );

    return () =>
      window.clearTimeout(
        timer,
      );
  }, [
    page,
    propertyId,
    buildingId,
    unitId,
    search,
  ]);


  function clearFilters() {
    setPropertyId("");
    setBuildingId("");
    setUnitId("");
    setSearch("");
    setPage(1);
  }


  return (
    <div>
      <section className="rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <LocationFields
            structure={structure}
            propertyId={propertyId}
            buildingId={buildingId}
            unitId={unitId}
            onPropertyChange={(value) => {
              setPropertyId(value);
              setPage(1);
            }}
            onBuildingChange={(value) => {
              setBuildingId(value);
              setPage(1);
            }}
            onUnitChange={(value) => {
              setUnitId(value);
              setPage(1);
            }}
            allowAll
          />

          <FormField label="Tenant">
            <div className="relative">
              <Search
                size={16}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-celestial dark:text-ash"
              />

              <input
                value={search}
                onChange={(event) => {
                  setSearch(
                    event.target.value,
                  );
                  setPage(1);
                }}
                placeholder="Name or email"
                className={`${controlClass} pl-10`}
              />
            </div>
          </FormField>
        </div>

        <button
          type="button"
          onClick={clearFilters}
          className="mt-4 flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold text-celestial transition hover:bg-cyan/30 hover:text-deep-blue dark:text-ash dark:hover:bg-moss"
        >
          <FilterX size={15} />
          Clear filters
        </button>
      </section>

      {error && (
        <div className="mt-5 rounded-2xl bg-red-50 p-4 text-sm text-red-600 dark:bg-red-400/10 dark:text-red-300">
          {error}
        </div>
      )}

      {!loading &&
        !error &&
        !data.items.length && (
          <div className="mt-5 rounded-[2rem] border border-dashed border-celestial/15 bg-white p-9 text-center dark:border-ash/15 dark:bg-dark-card">
            <UserRound
              size={30}
              className="mx-auto text-celestial dark:text-ash"
            />

            <h2 className="mt-4 text-lg font-semibold text-deep-blue dark:text-white">
              No current tenants
            </h2>

            <p className="mt-1 text-sm text-deep-blue/45 dark:text-white/40">
              A tenant appears here after they are assigned to one of your units through an active lease.
            </p>
          </div>
        )}

      {!!data.items.length && (
        <div className="mt-5 overflow-hidden rounded-[2rem] border border-celestial/10 bg-white dark:border-ash/10 dark:bg-dark-card">
          <div className="hidden grid-cols-[1.3fr_1.3fr_1.5fr_1fr_1fr] gap-4 border-b border-celestial/10 px-5 py-4 text-[10px] font-bold uppercase tracking-[0.12em] text-deep-blue/35 lg:grid dark:border-ash/10 dark:text-white/35">
            <span>Tenant</span>
            <span>Contact</span>
            <span>Home</span>
            <span>Lease</span>
            <span>Monthly rent</span>
          </div>

          {data.items.map(
            (item) => {
              const name =
                [
                  item.tenant.first_name,
                  item.tenant.last_name,
                ]
                  .filter(Boolean)
                  .join(" ");

              return (
                <article
                  key={item.lease_id}
                  className="grid gap-4 border-b border-celestial/8 p-5 last:border-b-0 lg:grid-cols-[1.3fr_1.3fr_1.5fr_1fr_1fr] lg:items-center dark:border-ash/8"
                >
                  <div className="flex items-center gap-3">
                    <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                      <UserRound size={18} />
                    </div>

                    <div>
                      <p className="font-semibold text-deep-blue dark:text-white">
                        {name || item.tenant.email}
                      </p>

                      <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.12em] text-moss dark:text-lime-soft">
                        Current tenant
                      </p>
                    </div>
                  </div>

                  <div className="space-y-1.5 text-xs text-deep-blue/55 dark:text-white/50">
                    <p className="flex items-center gap-2">
                      <Mail size={13} />
                      {item.tenant.email}
                    </p>

                    <p className="flex items-center gap-2">
                      <Phone size={13} />
                      {item.tenant.phone_number ?? "No phone number"}
                    </p>
                  </div>

                  <div>
                    <p className="flex items-center gap-2 text-sm font-semibold text-deep-blue dark:text-white">
                      <MapPin size={14} />
                      {item.property_name}
                    </p>

                    <p className="mt-1 text-xs text-deep-blue/45 dark:text-white/40">
                      {item.building_name}
                      {" · Unit "}
                      {item.unit_number}
                    </p>
                  </div>

                  <div className="text-xs text-deep-blue/50 dark:text-white/45">
                    <p>{item.start_date}</p>
                    <p className="mt-1">
                      → {item.end_date ?? "Current"}
                    </p>
                  </div>

                  <p className="font-semibold text-deep-blue dark:text-white">
                    {Number(item.rent_amount).toFixed(2)}
                  </p>
                </article>
              );
            },
          )}
        </div>
      )}

      {loading && (
        <p className="mt-5 text-sm text-deep-blue/45 dark:text-white/40">
          Loading tenants...
        </p>
      )}

      <Pagination
        meta={data.meta}
        onChange={setPage}
      />
    </div>
  );
}
