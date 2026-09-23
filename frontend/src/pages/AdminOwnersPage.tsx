import {
  Ban,
  CheckCircle2,
  FilterX,
  Mail,
  Phone,
  Search,
  ShieldCheck,
} from "lucide-react";

import {
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  FormField,
  controlClass,
} from "../components/FormField";

import {
  Pagination,
} from "../components/Pagination";

import {
  apiRequest,
} from "../lib/api";

import {
  confirmAction,
  errorAlert,
  successAlert,
} from "../lib/alerts";

import type {
  AdminOwnerItem,
  AdminOwnerPage,
} from "../types/admin";


const EMPTY_META = {
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
};


export default function AdminOwnersPage() {
  const [
    data,
    setData,
  ] = useState<AdminOwnerPage>({
    items: [],
    meta: EMPTY_META,
  });

  const [
    page,
    setPage,
  ] = useState(1);

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    statusFilter,
    setStatusFilter,
  ] = useState<
    "ALL" | "ACTIVE" | "INACTIVE"
  >("ALL");

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  async function load() {
    const params =
      new URLSearchParams({
        page: String(page),
        page_size: "10",
      });

    if (search.trim()) {
      params.set(
        "search",
        search.trim(),
      );
    }

    if (
      statusFilter ===
      "ACTIVE"
    ) {
      params.set(
        "active",
        "true",
      );
    }

    if (
      statusFilter ===
      "INACTIVE"
    ) {
      params.set(
        "active",
        "false",
      );
    }

    setLoading(true);
    setError("");

    try {
      setData(
        await apiRequest<
          AdminOwnerPage
        >(
          `/admin/owners?${params}`,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load owners.",
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
    search,
    statusFilter,
  ]);


  async function changeStatus(
    owner: AdminOwnerItem,
  ) {
    const nextActive =
      !owner.is_active;

    const confirmed =
      await confirmAction({
        title:
          nextActive
            ? "Reactivate owner?"
            : "Deactivate owner?",

        text:
          nextActive
            ? "The owner will be able to sign in again."
            : "The owner will be blocked from signing in. Their properties, tenants, leases, payments, and history will remain stored.",

        confirmText:
          nextActive
            ? "Reactivate"
            : "Deactivate",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        (
          "/admin/owners/"
          + owner.id
          + "/status"
        ),
        {
          method: "PATCH",
          body:
            JSON.stringify({
              is_active:
                nextActive,
            }),
        },
      );

      successAlert(
        nextActive
          ? "Owner reactivated"
          : "Owner deactivated",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Unable to update owner",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  function clearFilters() {
    setSearch("");
    setStatusFilter("ALL");
    setPage(1);
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
          Administration
        </p>

        <h1 className="mt-2 text-4xl font-semibold tracking-[-0.055em] text-deep-blue dark:text-white">
          Owners
        </h1>

        <p className="mt-2 text-sm text-deep-blue/50 dark:text-white/45">
          View owner accounts, portfolio size, and account access status.
        </p>
      </div>


      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
        <div className="grid gap-4 md:grid-cols-[1.5fr_1fr]">
          <FormField label="Search owners">
            <div className="relative">
              <Search
                size={16}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-celestial dark:text-ash"
              />

              <input
                value={search}
                onChange={(
                  event,
                ) => {
                  setSearch(
                    event.target
                      .value,
                  );
                  setPage(1);
                }}
                placeholder="Name, email, or phone"
                className={`${controlClass} pl-10`}
              />
            </div>
          </FormField>

          <FormField label="Account status">
            <select
              value={
                statusFilter
              }
              onChange={(
                event,
              ) => {
                setStatusFilter(
                  event.target
                    .value as
                    | "ALL"
                    | "ACTIVE"
                    | "INACTIVE",
                );
                setPage(1);
              }}
              className={
                controlClass
              }
            >
              <option value="ALL">
                All owners
              </option>

              <option value="ACTIVE">
                Active
              </option>

              <option value="INACTIVE">
                Inactive
              </option>
            </select>
          </FormField>
        </div>

        <button
          type="button"
          onClick={
            clearFilters
          }
          className="mt-4 flex items-center gap-2 text-xs font-semibold text-celestial dark:text-ash"
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


      <div className="mt-6 overflow-hidden rounded-[2rem] border border-celestial/10 bg-white dark:border-ash/10 dark:bg-dark-card">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1050px] border-collapse">
            <thead>
              <tr className="border-b border-celestial/10 bg-cyan/20 text-left dark:border-ash/10 dark:bg-moss/45">
                <Head>
                  Owner
                </Head>

                <Head>
                  Contact
                </Head>

                <Head>
                  Properties
                </Head>

                <Head>
                  Buildings
                </Head>

                <Head>
                  Units
                </Head>

                <Head>
                  Active leases
                </Head>

                <Head>
                  Status
                </Head>

                <Head align="right">
                  Action
                </Head>
              </tr>
            </thead>

            <tbody>
              {data.items.map(
                (owner) => {
                  const name =
                    [
                      owner.first_name,
                      owner.last_name,
                    ]
                      .filter(Boolean)
                      .join(" ");

                  return (
                    <tr
                      key={owner.id}
                      className="border-b border-celestial/8 last:border-b-0 dark:border-ash/8"
                    >
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <div className="grid size-10 place-items-center rounded-xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                            <ShieldCheck
                              size={16}
                            />
                          </div>

                          <div>
                            <p className="font-semibold text-deep-blue dark:text-white">
                              {name ||
                                owner.email}
                            </p>

                            <p className="mt-1 text-xs text-deep-blue/35 dark:text-white/35">
                              Joined{" "}
                              {new Date(
                                owner.created_at,
                              ).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </td>

                      <td className="px-5 py-4">
                        <div className="space-y-1.5 text-xs text-deep-blue/50 dark:text-white/45">
                          <p className="flex items-center gap-2">
                            <Mail
                              size={13}
                            />
                            {
                              owner.email
                            }
                          </p>

                          <p className="flex items-center gap-2">
                            <Phone
                              size={13}
                            />
                            {
                              owner.phone_number ??
                              "No phone"
                            }
                          </p>
                        </div>
                      </td>

                      <CountCell
                        value={
                          owner.property_count
                        }
                      />

                      <CountCell
                        value={
                          owner.building_count
                        }
                      />

                      <CountCell
                        value={
                          owner.unit_count
                        }
                      />

                      <CountCell
                        value={
                          owner.active_lease_count
                        }
                      />

                      <td className="px-5 py-4">
                        <span
                          className={[
                            "inline-flex rounded-full px-3 py-1 text-[9px] font-bold uppercase tracking-[0.12em]",
                            owner.is_active
                              ? "bg-moss/10 text-moss dark:bg-lime-soft/10 dark:text-lime-soft"
                              : "bg-red-50 text-red-600 dark:bg-red-400/10 dark:text-red-300",
                          ].join(
                            " ",
                          )}
                        >
                          {owner.is_active
                            ? "Active"
                            : "Inactive"}
                        </span>
                      </td>

                      <td className="px-5 py-4 text-right">
                        <button
                          type="button"
                          onClick={() =>
                            changeStatus(
                              owner,
                            )
                          }
                          className={[
                            "inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold transition",
                            owner.is_active
                              ? "text-red-600 hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-400/10"
                              : "bg-cyan/40 text-deep-blue hover:bg-cyan dark:bg-moss dark:text-lime-soft",
                          ].join(
                            " ",
                          )}
                        >
                          {owner.is_active
                            ? (
                              <Ban
                                size={14}
                              />
                            )
                            : (
                              <CheckCircle2
                                size={14}
                              />
                            )}

                          {owner.is_active
                            ? "Deactivate"
                            : "Reactivate"}
                        </button>
                      </td>
                    </tr>
                  );
                },
              )}

              {!loading &&
                !data.items.length && (
                <tr>
                  <td
                    colSpan={8}
                    className="px-5 py-14 text-center text-sm text-deep-blue/40 dark:text-white/35"
                  >
                    No owners match the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>


      {loading && (
        <p className="mt-4 text-sm text-deep-blue/40 dark:text-white/35">
          Loading owners...
        </p>
      )}


      <Pagination
        meta={data.meta}
        onChange={setPage}
      />
    </div>
  );
}


function Head({
  children,
  align = "left",
}: {
  children:
    ReactNode;

  align?:
    "left" | "right";
}) {
  return (
    <th
      className={[
        "px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/45 dark:text-lime-soft/60",
        align === "right"
          ? "text-right"
          : "text-left",
      ].join(" ")}
    >
      {children}
    </th>
  );
}


function CountCell({
  value,
}: {
  value: number;
}) {
  return (
    <td className="px-5 py-4 text-sm font-semibold text-deep-blue dark:text-white">
      {value}
    </td>
  );
}
