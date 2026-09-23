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
  AdminSubscriptionPaymentPage,
  SubscriptionPaymentStatus,
} from "../types/subscription";


const EMPTY_META = {
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
};


function money(
  value:
    | string
    | number,
  currency: string,
) {
  return new Intl
    .NumberFormat(
      "en-US",
      {
        style: "currency",
        currency:
          currency.toUpperCase(),
        maximumFractionDigits: 2,
      },
    )
    .format(
      Number(value),
    );
}


export default function AdminSubscriptionPaymentsPage() {
  const [
    data,
    setData,
  ] = useState<
    AdminSubscriptionPaymentPage
  >({
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
    "ALL"
    | SubscriptionPaymentStatus
  >("ALL");

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
        "payment_status",
        statusFilter,
      );
    }

    setLoading(true);

    try {
      setData(
        await apiRequest<
          AdminSubscriptionPaymentPage
        >(
          (
            "/admin/"
            + "subscription-payments?"
            + params
          ),
        ),
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


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
          Administration
        </p>

        <h1 className="mt-2 text-4xl font-semibold tracking-[-0.055em] text-deep-blue dark:text-white">
          Subscription payments
        </h1>

        <p className="mt-2 text-sm text-deep-blue/50 dark:text-white/45">
          Review recurring Stripe invoice results across owner subscriptions.
        </p>
      </div>


      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
        <div className="grid gap-4 md:grid-cols-[1.5fr_1fr]">
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
                placeholder="Owner or invoice ID"
                className={`${controlClass} pl-10`}
              />
            </div>
          </FormField>

          <FormField label="Payment status">
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
                    | SubscriptionPaymentStatus,
                );
                setPage(1);
              }}
              className={
                controlClass
              }
            >
              <option value="ALL">
                All payments
              </option>

              <option value="PAID">
                Paid
              </option>

              <option value="FAILED">
                Failed
              </option>
            </select>
          </FormField>
        </div>

        <button
          type="button"
          onClick={() => {
            setSearch("");
            setStatusFilter(
              "ALL",
            );
            setPage(1);
          }}
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
          <table className="w-full min-w-[900px] border-collapse">
            <thead>
              <tr className="border-b border-celestial/10 bg-cyan/20 text-left dark:border-ash/10 dark:bg-moss/45">
                {[
                  "Date",
                  "Owner",
                  "Plan",
                  "Amount",
                  "Invoice",
                  "Status",
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

                  return (
                    <tr
                      key={item.id}
                      className="border-b border-celestial/8 last:border-b-0 dark:border-ash/8"
                    >
                      <td className="px-5 py-4 text-sm text-deep-blue/50 dark:text-white/45">
                        {new Date(
                          item.created_at,
                        ).toLocaleDateString()}
                      </td>

                      <td className="px-5 py-4">
                        <p className="font-semibold text-deep-blue dark:text-white">
                          {name ||
                            item.owner_email}
                        </p>

                        <p className="mt-1 text-xs text-deep-blue/40 dark:text-white/35">
                          {item.owner_email}
                        </p>
                      </td>

                      <td className="px-5 py-4 text-sm font-semibold text-deep-blue dark:text-white">
                        {item.plan_name}
                      </td>

                      <td className="px-5 py-4 text-sm font-semibold text-deep-blue dark:text-white">
                        {money(
                          item.amount,
                          item.currency,
                        )}
                      </td>

                      <td className="px-5 py-4 text-xs text-deep-blue/45 dark:text-white/40">
                        {item.stripe_invoice_id}
                      </td>

                      <td className="px-5 py-4">
                        <span
                          className={[
                            "rounded-full px-3 py-1 text-[9px] font-bold uppercase tracking-[0.11em]",
                            item.status
                            === "PAID"
                              ? "bg-moss/10 text-moss dark:bg-lime-soft/10 dark:text-lime-soft"
                              : "bg-red-50 text-red-600 dark:bg-red-400/10 dark:text-red-300",
                          ].join(" ")}
                        >
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  );
                },
              )}

              {!loading &&
                !data.items.length && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-5 py-14 text-center text-sm text-deep-blue/40 dark:text-white/35"
                  >
                    No subscription payments found.
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
