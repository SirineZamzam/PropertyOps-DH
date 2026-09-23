import {
  BadgeDollarSign,
  CalendarDays,
  Check,
  CreditCard,
  Infinity,
  RotateCcw,
  ShieldCheck,
  WalletCards,
} from "lucide-react";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useSearchParams,
} from "react-router";

import {
  apiRequest,
} from "../lib/api";

import {
  confirmAction,
  errorAlert,
  successAlert,
} from "../lib/alerts";

import type {
  BillingInterval,
  OwnerSubscription,
  SubscriptionPaymentItem,
  SubscriptionPlan,
} from "../types/subscription";


function money(
  value:
    | string
    | number,
  currency = "USD",
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


function statusClass(
  status: string,
) {
  if (
    status === "ACTIVE"
    || status === "FREE"
    || status === "PAID"
  ) {
    return (
      "bg-moss/10 text-moss "
      + "dark:bg-lime-soft/10 "
      + "dark:text-lime-soft"
    );
  }

  if (
    status === "PAST_DUE"
    || status === "FAILED"
  ) {
    return (
      "bg-red-50 text-red-600 "
      + "dark:bg-red-400/10 "
      + "dark:text-red-300"
    );
  }

  return (
    "bg-amber-50 text-amber-700 "
    + "dark:bg-amber-300/10 "
    + "dark:text-amber-200"
  );
}


export default function OwnerSubscriptionPage() {
  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams();

  const [
    subscription,
    setSubscription,
  ] = useState<
    OwnerSubscription | null
  >(null);

  const [
    plans,
    setPlans,
  ] = useState<
    SubscriptionPlan[]
  >([]);

  const [
    payments,
    setPayments,
  ] = useState<
    SubscriptionPaymentItem[]
  >([]);

  const [
    billing,
    setBilling,
  ] = useState<
    BillingInterval
  >("MONTHLY");

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    actionPlanId,
    setActionPlanId,
  ] = useState<
    number | null
  >(null);


  async function load() {
    setLoading(true);

    try {
      const [
        current,
        availablePlans,
        paymentHistory,
      ] = await Promise.all([
        apiRequest<
          OwnerSubscription
        >(
          "/owner/subscription",
        ),

        apiRequest<
          SubscriptionPlan[]
        >(
          "/subscription-plans",
        ),

        apiRequest<
          SubscriptionPaymentItem[]
        >(
          "/owner/subscription/payments",
        ),
      ]);

      setSubscription(
        current,
      );

      setPlans(
        availablePlans,
      );

      setPayments(
        paymentHistory,
      );

      if (
        current.billing_interval
      ) {
        setBilling(
          current.billing_interval,
        );
      }
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    async function handleReturn() {
      const result =
        searchParams.get(
          "subscription",
        );

      if (
        result === "cancelled"
      ) {
        try {
          await apiRequest(
            (
              "/owner/subscription/"
              + "checkout-cancelled"
            ),
            {
              method: "POST",
            },
          );

          successAlert(
            "Checkout cancelled",
            "No paid subscription was activated.",
          );
        } catch {
          // Page reload below will still show
          // the authoritative local status.
        }
      }

      if (
        result === "success"
      ) {
        successAlert(
          "Checkout completed",
          "Stripe received your checkout. Paid access activates after verified webhook confirmation.",
        );
      }

      if (result) {
        setSearchParams(
          {},
          {
            replace: true,
          },
        );
      }

      await load();
    }

    void handleReturn();
  }, []);


  const usageText =
    useMemo(
      () => {
        if (!subscription) {
          return "—";
        }

        const limit =
          subscription
            .effective_max_properties;

        if (limit === null) {
          return (
            `${subscription.property_count} / Unlimited`
          );
        }

        return (
          `${subscription.property_count} / ${limit}`
        );
      },
      [
        subscription,
      ],
    );


  async function refreshAfterAction() {
    await load();

    window.dispatchEvent(
      new Event(
        "propertyops-subscription-updated",
      ),
    );
  }


  async function choosePlan(
    plan: SubscriptionPlan,
  ) {
    if (!subscription) {
      return;
    }

    if (
      subscription.status
      === "INCOMPLETE"
    ) {
      await errorAlert(
        "Subscription pending",
        "Wait for Stripe confirmation before starting another subscription change.",
      );

      return;
    }

    setActionPlanId(
      plan.id,
    );

    try {
      if (
        plan.code === "FREE"
      ) {
        if (
          subscription.status
          === "FREE"
          && subscription
            .plan.code
            === "FREE"
        ) {
          return;
        }

        if (
          subscription.status
          === "ACTIVE"
          || subscription.status
          === "PAST_DUE"
        ) {
          const confirmed =
            await confirmAction({
              title:
                "Move to Free?",

              text:
                (
                  "Your paid subscription "
                  + "will remain available "
                  + "until the end of the "
                  + "current billing period, "
                  + "then paid access ends."
                ),

              confirmText:
                "Schedule cancellation",
            });

          if (!confirmed) {
            return;
          }

          await apiRequest(
            "/owner/subscription/cancel",
            {
              method: "POST",
            },
          );

          successAlert(
            "Cancellation scheduled",
            "Your paid plan remains active until the end of the current billing period.",
          );

          await refreshAfterAction();

          return;
        }

        await apiRequest(
          "/owner/subscription/use-free",
          {
            method: "POST",
          },
        );

        successAlert(
          "Free plan active",
        );

        await refreshAfterAction();

        return;
      }


      if (
        subscription.status
        === "ACTIVE"
        && subscription
          .plan.code
          !== "FREE"
      ) {
        const samePlan =
          subscription.plan.id
          === plan.id;

        const sameBilling =
          subscription
            .billing_interval
          === billing;

        if (
          samePlan
          && sameBilling
        ) {
          return;
        }

        const confirmed =
          await confirmAction({
            title:
              samePlan
                ? "Change billing cycle?"
                : `Switch to ${plan.name}?`,

            text:
              (
                "Stripe will update the "
                + "existing subscription. "
                + "Your subscription status "
                + "will remain authoritative "
                + "from Stripe."
              ),

            confirmText:
              "Confirm change",
          });

        if (!confirmed) {
          return;
        }

        await apiRequest(
          "/owner/subscription/change",
          {
            method: "POST",

            body:
              JSON.stringify({
                plan_id:
                  plan.id,

                billing_interval:
                  billing,
              }),
          },
        );

        successAlert(
          "Subscription updated",
          "The change was submitted to Stripe.",
        );

        await refreshAfterAction();

        return;
      }


      const response =
        await apiRequest<{
          checkout_url: string;
        }>(
          "/owner/subscription/checkout",
          {
            method: "POST",

            body:
              JSON.stringify({
                plan_id:
                  plan.id,

                billing_interval:
                  billing,
              }),
          },
        );

      window.location.assign(
        response.checkout_url,
      );
    } catch (error) {
      await errorAlert(
        "Subscription action failed",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    } finally {
      setActionPlanId(null);
    }
  }


  async function keepSubscription() {
    try {
      await apiRequest(
        "/owner/subscription/resume",
        {
          method: "POST",
        },
      );

      successAlert(
        "Subscription kept",
        "The scheduled cancellation was removed.",
      );

      await refreshAfterAction();
    } catch (error) {
      await errorAlert(
        "Unable to keep subscription",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  if (
    loading
    || !subscription
  ) {
    return (
      <p className="text-sm text-deep-blue/45 dark:text-white/40">
        Loading subscription...
      </p>
    );
  }


  const renewal =
    subscription
      .current_period_end
      ? new Date(
          subscription
            .current_period_end,
        ).toLocaleDateString()
      : "—";


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
          Billing
        </p>

        <h1 className="mt-2 text-4xl font-semibold tracking-[-0.055em] text-deep-blue dark:text-white">
          Subscription
        </h1>

        <p className="mt-2 text-sm text-deep-blue/50 dark:text-white/45">
          Manage your plan, property allowance, billing cycle, and subscription payment history.
        </p>
      </div>


      <div className="mt-8 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="rounded-[2rem] bg-celestial p-7 text-white dark:bg-phthalo">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] opacity-60">
                Current plan
              </p>

              <h2 className="mt-2 text-4xl font-semibold tracking-[-0.05em]">
                {subscription.plan.name}
              </h2>

              <p className="mt-2 text-sm opacity-65">
                {subscription.billing_interval
                  ? subscription
                      .billing_interval
                      .toLowerCase()
                  : "No recurring billing"}
              </p>
            </div>

            <span
              className={[
                "rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-[0.12em]",
                subscription.status
                  === "ACTIVE"
                  || subscription.status
                  === "FREE"
                  ? "bg-white/18 text-white"
                  : "bg-black/15 text-white",
              ].join(" ")}
            >
              {subscription.status}
            </span>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <Info
              icon={BadgeDollarSign}
              label="Plan"
              value={
                subscription.plan.code
              }
            />

            <Info
              icon={CalendarDays}
              label="Period end"
              value={renewal}
            />

            <Info
              icon={ShieldCheck}
              label="Property usage"
              value={usageText}
            />
          </div>

          {subscription
            .cancel_at_period_end && (
            <div className="mt-5 rounded-2xl bg-white/12 p-4">
              <p className="text-sm font-semibold">
                Cancellation scheduled
              </p>

              <p className="mt-1 text-xs text-white/65">
                Your plan stays active until the current billing period ends.
              </p>

              <button
                type="button"
                onClick={
                  keepSubscription
                }
                className="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-semibold text-deep-blue"
              >
                <RotateCcw
                  size={14}
                />
                Keep subscription
              </button>
            </div>
          )}

          {subscription.status
            === "INCOMPLETE" && (
            <div className="mt-5 rounded-2xl bg-white/12 p-4 text-sm">
              Stripe verification is still pending. Paid limits are not enabled until the webhook confirms the subscription.
            </div>
          )}

          {subscription.status
            === "PAST_DUE" && (
            <div className="mt-5 rounded-2xl bg-red-950/20 p-4 text-sm">
              Stripe reported a payment issue. New property creation currently uses the Free-plan limit until billing becomes active again.
            </div>
          )}
        </section>


        <section className="rounded-[2rem] border border-celestial/10 bg-white p-6 dark:border-ash/10 dark:bg-dark-card">
          <WalletCards
            size={24}
            className="text-celestial dark:text-ash"
          />

          <p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-deep-blue/35 dark:text-white/35">
            Current allowance
          </p>

          <p className="mt-2 text-3xl font-semibold text-deep-blue dark:text-white">
            {usageText}
          </p>

          <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
            Existing properties are never deleted if your plan changes. The limit controls creation of new properties.
          </p>
        </section>
      </div>


      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-6 dark:border-ash/10 dark:bg-dark-card">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-celestial dark:text-ash">
              Plans
            </p>

            <h2 className="mt-2 text-2xl font-semibold text-deep-blue dark:text-white">
              Choose the right capacity
            </h2>
          </div>

          <div className="inline-flex self-start rounded-2xl bg-cyan/35 p-1 dark:bg-moss/50">
            {(
              [
                "MONTHLY",
                "YEARLY",
              ] as const
            ).map(
              (interval) => (
                <button
                  key={interval}
                  type="button"
                  onClick={() =>
                    setBilling(
                      interval,
                    )
                  }
                  className={[
                    "rounded-xl px-4 py-2.5 text-xs font-semibold transition",
                    billing ===
                    interval
                      ? "bg-white text-deep-blue shadow-sm dark:bg-phthalo dark:text-white"
                      : "text-deep-blue/55 dark:text-lime-soft/60",
                  ].join(" ")}
                >
                  {interval ===
                  "MONTHLY"
                    ? "Monthly"
                    : "Yearly"}
                </button>
              ),
            )}
          </div>
        </div>


        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          {plans.map(
            (plan) => {
              const price =
                billing ===
                "MONTHLY"
                  ? plan.monthly_price
                  : plan.yearly_price;

              const samePlan =
                subscription.plan.id
                === plan.id;

              const sameBilling =
                subscription
                  .billing_interval
                === billing;

              const current =
                samePlan
                && (
                  plan.code
                  === "FREE"
                  || (
                    subscription.status
                    === "ACTIVE"
                    && sameBilling
                  )
                );

              return (
                <article
                  key={plan.id}
                  className={[
                    "rounded-[1.7rem] border p-5",
                    samePlan
                      ? "border-celestial/35 bg-cyan/10 dark:border-ash/30 dark:bg-moss/15"
                      : "border-celestial/10 bg-light-canvas dark:border-ash/10 dark:bg-phthalo",
                  ].join(" ")}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-celestial dark:text-ash">
                        {plan.code}
                      </p>

                      <h3 className="mt-1 text-xl font-semibold text-deep-blue dark:text-white">
                        {plan.name}
                      </h3>
                    </div>

                    {samePlan && (
                      <span className="rounded-full bg-cyan px-3 py-1 text-[9px] font-bold uppercase tracking-[0.11em] text-deep-blue dark:bg-moss dark:text-lime-soft">
                        Selected
                      </span>
                    )}
                  </div>

                  <p className="mt-5 text-3xl font-semibold text-deep-blue dark:text-white">
                    {plan.code ===
                    "FREE"
                      ? "$0"
                      : money(
                          price,
                        )}
                  </p>

                  <p className="mt-2 flex items-center gap-2 text-sm text-deep-blue/50 dark:text-white/45">
                    <Check
                      size={15}
                      className="text-moss dark:text-lime-soft"
                    />

                    {plan.max_properties ===
                    null ? (
                      <>
                        <Infinity
                          size={15}
                        />
                        Unlimited properties
                      </>
                    ) : (
                      `${plan.max_properties} properties`
                    )}
                  </p>

                  <button
                    type="button"
                    disabled={
                      current
                      || actionPlanId
                        !== null
                      || subscription
                        .status
                        === "INCOMPLETE"
                    }
                    onClick={() =>
                      choosePlan(
                        plan,
                      )
                    }
                    className="mt-6 w-full rounded-xl bg-celestial px-4 py-3 text-xs font-semibold text-white transition hover:bg-cyan hover:text-deep-blue disabled:cursor-not-allowed disabled:opacity-45 dark:bg-moss dark:text-lime-soft"
                  >
                    {current
                      ? "Current"
                      : actionPlanId
                        === plan.id
                        ? "Working..."
                        : plan.code
                          === "FREE"
                          ? (
                            subscription.status
                            === "ACTIVE"
                              ? "Move to Free"
                              : "Use Free"
                          )
                          : (
                            subscription.status
                            === "ACTIVE"
                              ? (
                                samePlan
                                  ? "Change billing"
                                  : "Switch plan"
                              )
                              : "Subscribe"
                          )}
                  </button>
                </article>
              );
            },
          )}
        </div>
      </section>


      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-6 dark:border-ash/10 dark:bg-dark-card">
        <div className="flex items-center gap-3">
          <div className="grid size-11 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
            <CreditCard
              size={19}
            />
          </div>

          <div>
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-celestial dark:text-ash">
              Billing history
            </p>

            <h2 className="mt-1 text-xl font-semibold text-deep-blue dark:text-white">
              Subscription payments
            </h2>
          </div>
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[680px] border-collapse">
            <thead>
              <tr className="border-b border-celestial/10 text-left dark:border-ash/10">
                {[
                  "Date",
                  "Plan",
                  "Amount",
                  "Invoice",
                  "Status",
                ].map(
                  (label) => (
                    <th
                      key={label}
                      className="px-4 py-3 text-[10px] font-bold uppercase tracking-[0.12em] text-deep-blue/35 dark:text-white/35"
                    >
                      {label}
                    </th>
                  ),
                )}
              </tr>
            </thead>

            <tbody>
              {payments.map(
                (payment) => (
                  <tr
                    key={payment.id}
                    className="border-b border-celestial/8 last:border-b-0 dark:border-ash/8"
                  >
                    <td className="px-4 py-4 text-sm text-deep-blue/50 dark:text-white/45">
                      {new Date(
                        payment.created_at,
                      ).toLocaleDateString()}
                    </td>

                    <td className="px-4 py-4 text-sm font-semibold text-deep-blue dark:text-white">
                      {payment.plan_name}
                    </td>

                    <td className="px-4 py-4 text-sm font-semibold text-deep-blue dark:text-white">
                      {money(
                        payment.amount,
                        payment.currency,
                      )}
                    </td>

                    <td className="px-4 py-4 text-xs text-deep-blue/45 dark:text-white/40">
                      {payment.stripe_invoice_id}
                    </td>

                    <td className="px-4 py-4">
                      <span
                        className={[
                          "rounded-full px-3 py-1 text-[9px] font-bold uppercase tracking-[0.11em]",
                          statusClass(
                            payment.status,
                          ),
                        ].join(" ")}
                      >
                        {payment.status}
                      </span>
                    </td>
                  </tr>
                ),
              )}

              {!payments.length && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-4 py-10 text-center text-sm text-deep-blue/40 dark:text-white/35"
                  >
                    No subscription payments yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}


function Info({
  icon: Icon,
  label,
  value,
}: {
  icon:
    typeof BadgeDollarSign;

  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl bg-white/12 p-4">
      <Icon
        size={17}
      />

      <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.12em] opacity-55">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold">
        {value}
      </p>
    </div>
  );
}
