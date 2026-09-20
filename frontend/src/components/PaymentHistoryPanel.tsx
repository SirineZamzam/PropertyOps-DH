import {
  CheckCircle2,
  CircleX,
  Clock3,
  CreditCard,
  RefreshCw,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  apiRequest,
} from "../lib/api";


type PaymentStatus =
  | "PENDING"
  | "PROCESSING"
  | "PAID"
  | "FAILED"
  | "EXPIRED";


interface PaymentHistoryItem {
  id: number;

  rent_obligation_id: number;

  amount:
    | string
    | number;

  currency: string;

  status:
    PaymentStatus;

  due_date: string;

  created_at: string;

  paid_at:
    | string
    | null;

  tenant_email?:
    string;

  tenant_first_name?:
    string | null;

  tenant_last_name?:
    string | null;

  property_name?:
    string;

  building_name?:
    string;

  unit_number?:
    string;
}


function formatDate(
  value:
    | string
    | null,
) {
  if (!value) {
    return "—";
  }

  const normalized =
    value.includes("T")
      ? value
      : `${value}T12:00:00`;

  return new Intl
    .DateTimeFormat(
      "en",
      {
        month: "short",
        day: "numeric",
        year: "numeric",
      },
    )
    .format(
      new Date(
        normalized,
      ),
    );
}


function statusStyle(
  status: PaymentStatus,
) {
  switch (status) {
    case "PAID":
      return (
        "bg-moss/10 text-moss " +
        "dark:bg-lime-soft/10 " +
        "dark:text-lime-soft"
      );

    case "FAILED":
    case "EXPIRED":
      return (
        "bg-red-50 text-red-600 " +
        "dark:bg-red-400/10 " +
        "dark:text-red-300"
      );

    default:
      return (
        "bg-celestial/10 " +
        "text-celestial " +
        "dark:bg-cyan/10 " +
        "dark:text-cyan"
      );
  }
}


function StatusIcon({
  status,
}: {
  status: PaymentStatus;
}) {
  if (
    status === "PAID"
  ) {
    return (
      <CheckCircle2
        size={15}
      />
    );
  }

  if (
    status === "FAILED" ||
    status === "EXPIRED"
  ) {
    return (
      <CircleX
        size={15}
      />
    );
  }

  return (
    <Clock3
      size={15}
    />
  );
}


export function PaymentHistoryPanel({
  mode,
  leaseId,
}: {
  mode:
    | "OWNER"
    | "TENANT";

  leaseId?: number;
}) {
  const [
    payments,
    setPayments,
  ] =
    useState<
      PaymentHistoryItem[]
    >([]);

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    error,
    setError,
  ] =
    useState("");


  async function load() {
    if (
      mode === "TENANT" &&
      !leaseId
    ) {
      setPayments([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const path =
        mode === "OWNER"
          ? "/owner/payments?limit=8"
          : `/tenant/homes/${leaseId}/payments`;

      const data =
        await apiRequest<
          PaymentHistoryItem[]
        >(path);

      setPayments(
        data,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load payments.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    load();
  }, [
    mode,
    leaseId,
  ]);


  return (
    <section
      className="
        mt-7
        rounded-[2rem]
        border
        border-celestial/10
        bg-white
        p-6
        dark:border-ash/10
        dark:bg-dark-card
      "
    >
      <div
        className="
          flex
          items-start
          justify-between
          gap-4
        "
      >
        <div>
          <p
            className="
              text-xs
              font-bold
              uppercase
              tracking-[0.18em]
              text-celestial
              dark:text-ash
            "
          >
            Payments
          </p>

          <h2
            className="
              mt-1
              text-xl
              font-semibold
              text-deep-blue
              dark:text-white
            "
          >
            {mode === "OWNER"
              ? "Recent payment activity"
              : "Payment history"}
          </h2>

          <p
            className="
              mt-1
              text-sm
              text-deep-blue/45
              dark:text-white/40
            "
          >
            {mode === "OWNER"
              ? "Stripe payment attempts across your properties."
              : "Your Stripe payment attempts and their verified status."}
          </p>
        </div>

        <button
          type="button"
          onClick={load}
          disabled={loading}
          title="Refresh payments"
          className="
            grid
            size-10
            place-items-center
            rounded-xl
            bg-cyan/40
            text-deep-blue
            transition
            hover:bg-cyan/70
            disabled:opacity-50
            dark:bg-moss
            dark:text-lime-soft
          "
        >
          <RefreshCw
            size={16}
            className={
              loading
                ? "animate-spin"
                : ""
            }
          />
        </button>
      </div>


      {error && (
        <div
          className="
            mt-5
            rounded-2xl
            bg-red-50
            p-4
            text-sm
            text-red-600
            dark:bg-red-400/10
            dark:text-red-300
          "
        >
          {error}
        </div>
      )}


      {!loading &&
        !error &&
        !payments.length && (
        <div
          className="
            mt-5
            rounded-2xl
            border
            border-dashed
            border-celestial/15
            p-7
            text-center
            text-sm
            text-deep-blue/40
            dark:border-ash/15
            dark:text-white/35
          "
        >
          No payment activity yet.
        </div>
      )}


      <div
        className="
          mt-5
          space-y-3
        "
      >
        {payments.map(
          (payment) => {
            const tenantName =
              [
                payment
                  .tenant_first_name,

                payment
                  .tenant_last_name,
              ]
                .filter(Boolean)
                .join(" ");

            return (
              <article
                key={payment.id}
                className="
                  flex
                  flex-col
                  gap-4
                  rounded-[1.4rem]
                  bg-light-canvas
                  p-4
                  sm:flex-row
                  sm:items-center
                  sm:justify-between
                  dark:bg-phthalo/40
                "
              >
                <div
                  className="
                    flex
                    items-start
                    gap-3
                  "
                >
                  <div
                    className="
                      grid
                      size-11
                      shrink-0
                      place-items-center
                      rounded-xl
                      bg-cyan/50
                      text-deep-blue
                      dark:bg-moss
                      dark:text-lime-soft
                    "
                  >
                    <CreditCard
                      size={18}
                    />
                  </div>

                  <div>
                    <div
                      className="
                        flex
                        flex-wrap
                        items-center
                        gap-2
                      "
                    >
                      <p
                        className="
                          font-semibold
                          text-deep-blue
                          dark:text-white
                        "
                      >
                        {payment.currency
                          .toUpperCase()}{" "}
                        {Number(
                          payment.amount,
                        ).toFixed(2)}
                      </p>

                      <span
                        className={[
                          "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.12em]",
                          statusStyle(
                            payment.status,
                          ),
                        ].join(
                          " ",
                        )}
                      >
                        <StatusIcon
                          status={
                            payment.status
                          }
                        />

                        {
                          payment.status
                        }
                      </span>
                    </div>

                    <p
                      className="
                        mt-1
                        text-xs
                        text-deep-blue/45
                        dark:text-white/40
                      "
                    >
                      Rent due{" "}
                      {formatDate(
                        payment.due_date,
                      )}
                    </p>

                    {mode ===
                      "OWNER" && (
                      <p
                        className="
                          mt-1
                          text-xs
                          text-deep-blue/45
                          dark:text-white/40
                        "
                      >
                        {tenantName ||
                          payment
                            .tenant_email}
                        {" · "}
                        {
                          payment
                            .property_name
                        }
                        {" · Unit "}
                        {
                          payment
                            .unit_number
                        }
                      </p>
                    )}
                  </div>
                </div>

                <div
                  className="
                    text-left
                    sm:text-right
                  "
                >
                  <p
                    className="
                      text-xs
                      font-semibold
                      text-deep-blue/50
                      dark:text-white/45
                    "
                  >
                    {payment.status ===
                      "PAID"
                      ? "Paid"
                      : "Attempted"}
                  </p>

                  <p
                    className="
                      mt-1
                      text-xs
                      text-deep-blue/35
                      dark:text-white/30
                    "
                  >
                    {formatDate(
                      payment.paid_at ??
                        payment.created_at,
                    )}
                  </p>
                </div>
              </article>
            );
          },
        )}
      </div>
    </section>
  );
}