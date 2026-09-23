import {
  FilterX,
  Search,
} from "lucide-react";

import {
  useEffect,
  useState,
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

import type {
  AdminSubscriptionPage,
  AdminSubscriptionSummary,
  SubscriptionPlan,
  SubscriptionStatus,
} from "../types/subscription";


const EMPTY_META = {
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
};


export default function AdminSubscriptionsPage() {
  const [
    summary,
    setSummary,
  ] = useState<
    AdminSubscriptionSummary | null
  >(null);

  const [
    plans,
    setPlans,
  ] = useState<
    SubscriptionPlan[]
  >([]);

  const [
    data,
    setData,
  ] = useState<AdminSubscriptionPage>({
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
    "ALL" | SubscriptionStatus
  >("ALL");

  const [
    planId,
    setPlanId,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);


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
      statusFilter
      !== "ALL"
    ) {
      params.set(
        "subscription_status",
        statusFilter,
      );
    }

    if (planId) {
      params.set(
        "plan_id",
        planId,
      );
    }

    setLoading(true);

    try {
      const [
        nextSummary,
        nextData,
      ] = await Promise.all([
        apiRequest<
          AdminSubscriptionSummary
        >(
          "/admin/subscriptions/summary",
        ),

        apiRequest<
          AdminSubscriptionPage
        >(
          `/admin/subscriptions?${params}`,
        ),
      ]);

      setSummary(
        nextSummary,
      );

      setData(
        nextData,
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    apiRequest<
      SubscriptionPlan[]
    >(
      "/admin/plans",
    )
      .then(setPlans)
      .catch(() =>
        setPlans([]),
      );
  }, []);


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
    planId,
  ]);


  function clearFilters() {
    setSearch("");
    setStatusFilter(
      "ALL",
    );
    setPlanId("");
    setPage(1);
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
          Administration
        </p>

        <h1 className="mt-2 text-4xl font-semibold tracking-[-0.055em] text-deep-blue dark:text-white">
          Subscriptions
        </h1>

        <p className="mt-2 text-sm text-deep-blue/50 dark:text-white/45">
          Monitor owner plans, billing states, renewal periods, and property usage.
        </p>
      </div>


      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <Metric
          label="Total"
          value={
            summary?.total ?? 0
          }
        />

        <Metric
          label="Free"
          value={
            summary?.free ?? 0
          }
        />

        <Metric
          label="Active paid"
          value={
            summary
              ?.active_paid ?? 0
          }
        />

        <Metric
          label="Pending"
          value={
            summary
              ?.incomplete ?? 0
          }
        />

        <Metric
          label="Past due"
          value={
            summary
              ?.past_due ?? 0
          }
        />
      </div>


      <section className="mt-6 rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
        <div className="grid gap-4 md:grid-cols-3">
          <FormField label="Search">
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
                    event.target.value,
                  );
                  setPage(1);
                }}
                placeholder="Owner name or email"
                className={`${controlClass} pl-10`}
              />
            </div>
          </FormField>

          <FormField label="Subscription status">
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
                    | SubscriptionStatus,
                );
                setPage(1);
              }}
              className={
                controlClass
              }
            >
              <option value="ALL">
                All statuses
              </option>

              <option value="FREE">
                Free
              </option>

              <option value="ACTIVE">
                Active
              </option>

              <option value="INCOMPLETE">
                Incomplete
              </option>

              <option value="PAST_DUE">
                Past due
              </option>

              <option value="CANCELED">
                Canceled
              </option>
            </select>
          </FormField>

          <FormField label="Plan">
            <select
              value={planId}
              onChange={(
                event,
              ) => {
                setPlanId(
                  event.target.value,
                );
                setPage(1);
              }}
              className={
                controlClass
              }
            >
              <option value="">
                All plans
              </option>

              {plans.map(
                (plan) => (
                  <option
                    key={plan.id}
                    value={plan.id}
                  >
                    {plan.name}
                  </option>
                ),
              )}
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
          <FilterX
            size={15}
          />
          Clear filters
        </button>
      </section>


      <div className="mt-6 overflow-hidden rounded-[2rem] border border-celestial/10 bg-white dark:border-ash/10 dark:bg-dark-card">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1100px] border-collapse">
            <thead>
              <tr className="border-b border-celestial/10 bg-cyan/20 text-left dark:border-ash/10 dark:bg-moss/45">
                {[
                  "Owner",
                  "Plan",
                  "Status",
                  "Billing",
                  "Usage",
                  "Period end",
                  "Cancellation",
                ].map(
                  (label) => (
                    <th
                      key={label}
                      className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.13em] text-deep-blue/45 dark:text-lime-soft/60"
                    >
                      {label}
                    </th>
                  ),
                )}
              </tr>
            </thead>

            <tbody>
              {data.items.map(
                (item) => {
                  const name =
                    [
                      item
                        .owner_first_name,
                      item
                        .owner_last_name,
                    ]
                      .filter(Boolean)
                      .join(" ");

                  const limit =
                    item
                      .max_properties;

                  return (
                    <tr
                      key={
                        item.owner_id
                      }
                      className="border-b border-celestial/8 last:border-b-0 dark:border-ash/8"
                    >
                      <td className="px-5 py-4">
                        <p className="font-semibold text-deep-blue dark:text-white">
                          {name ||
                            item.owner_email}
                        </p>

                        <p className="mt-1 text-xs text-deep-blue/40 dark:text-white/35">
                          {item.owner_email}
                        </p>
                      </td>

                      <td className="px-5 py-4">
                        <p className="font-semibold text-deep-blue dark:text-white">
                          {item.plan_name}
                        </p>

                        <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.1em] text-celestial dark:text-ash">
                          {item.plan_code}
                        </p>
                      </td>

                      <td className="px-5 py-4">
                        <Status
                          value={
                            item.status
                          }
                        />
                      </td>

                      <td className="px-5 py-4 text-sm text-deep-blue/55 dark:text-white/50">
                        {item.billing_interval ??
                          "—"}
                      </td>

                      <td className="px-5 py-4 text-sm font-semibold text-deep-blue dark:text-white">
                        {limit ===
                        null
                          ? `${item.property_count} / Unlimited`
                          : `${item.property_count} / ${limit}`}
                      </td>

                      <td className="px-5 py-4 text-sm text-deep-blue/50 dark:text-white/45">
                        {item.current_period_end
                          ? new Date(
                              item.current_period_end,
                            ).toLocaleDateString()
                          : "—"}
                      </td>

                      <td className="px-5 py-4 text-sm text-deep-blue/50 dark:text-white/45">
                        {item.cancel_at_period_end
                          ? "Scheduled"
                          : "No"}
                      </td>
                    </tr>
                  );
                },
              )}

              {!loading &&
                !data.items.length && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-5 py-14 text-center text-sm text-deep-blue/40 dark:text-white/35"
                  >
                    No subscriptions match these filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>


      <Pagination
        meta={data.meta}
        onChange={setPage}
      />
    </div>
  );
}


function Metric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-[1.6rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
      <p className="text-xs text-deep-blue/45 dark:text-white/40">
        {label}
      </p>

      <p className="mt-2 text-3xl font-semibold text-deep-blue dark:text-white">
        {value}
      </p>
    </div>
  );
}


function Status({
  value,
}: {
  value: string;
}) {
  const className =
    value === "ACTIVE"
    || value === "FREE"
      ? "bg-moss/10 text-moss dark:bg-lime-soft/10 dark:text-lime-soft"
      : value === "PAST_DUE"
        ? "bg-red-50 text-red-600 dark:bg-red-400/10 dark:text-red-300"
        : "bg-amber-50 text-amber-700 dark:bg-amber-300/10 dark:text-amber-200";

  return (
    <span
      className={`rounded-full px-3 py-1 text-[9px] font-bold uppercase tracking-[0.11em] ${className}`}
    >
      {value}
    </span>
  );
}
