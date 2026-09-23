import {
  ArrowRight,
  Building2,
  Check,
  Infinity,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router";

import {
  Brand,
} from "../components/Brand";

import {
  apiRequest,
} from "../lib/api";

import type {
  BillingInterval,
  SubscriptionPlan,
} from "../types/subscription";


export default function SignupPlanPage() {
  const navigate =
    useNavigate();

  const [
    plans,
    setPlans,
  ] = useState<
    SubscriptionPlan[]
  >([]);

  const [
    billing,
    setBilling,
  ] = useState<
    BillingInterval
  >("MONTHLY");

  const [
    loadingPlan,
    setLoadingPlan,
  ] = useState<
    number | null
  >(null);

  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {
    apiRequest<
      SubscriptionPlan[]
    >(
      "/subscription-plans",
    )
      .then(setPlans)
      .catch((err) =>
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load plans.",
        ),
      );
  }, []);


  async function choose(
    plan: SubscriptionPlan,
  ) {
    setError("");
    setLoadingPlan(
      plan.id,
    );

    try {
      if (
        plan.code === "FREE"
      ) {
        navigate(
          "/app",
          {
            replace: true,
          },
        );

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
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to continue.",
      );

      setLoadingPlan(null);
    }
  }


  return (
    <main className="min-h-screen bg-light-canvas p-5 text-deep-blue dark:bg-dark-canvas dark:text-white md:p-8">
      <div className="mx-auto max-w-6xl">
        <Brand />

        <div className="mt-10 text-center">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            One last step
          </p>

          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.055em] md:text-5xl">
            Choose your PropertyOps plan
          </h1>

          <p className="mx-auto mt-3 max-w-2xl text-sm text-deep-blue/50 dark:text-white/45">
            Start free or choose a paid plan. Paid plans activate only after Stripe confirms the subscription.
          </p>

          <div className="mt-6 inline-flex rounded-2xl bg-cyan/35 p-1 dark:bg-moss/45">
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
                    "rounded-xl px-5 py-2.5 text-sm font-semibold transition",
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


        {error && (
          <div className="mx-auto mt-6 max-w-2xl rounded-2xl bg-red-50 p-4 text-center text-sm text-red-600 dark:bg-red-400/10 dark:text-red-300">
            {error}
          </div>
        )}


        <div className="mt-8 grid gap-5 lg:grid-cols-3">
          {plans.map(
            (plan) => {
              const price =
                billing ===
                "MONTHLY"
                  ? Number(
                      plan.monthly_price,
                    )
                  : Number(
                      plan.yearly_price,
                    );

              const suffix =
                plan.code ===
                "FREE"
                  ? ""
                  : billing ===
                    "MONTHLY"
                    ? "/month"
                    : "/year";

              return (
                <article
                  key={plan.id}
                  className={[
                    "flex min-h-[390px] flex-col rounded-[2rem] border bg-white p-6 shadow-sm dark:bg-dark-card",
                    plan.code ===
                    "STANDARD"
                      ? "border-celestial/40 ring-4 ring-cyan/15 dark:border-ash/35"
                      : "border-celestial/10 dark:border-ash/10",
                  ].join(" ")}
                >
                  <div className="grid size-12 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                    <Building2
                      size={20}
                    />
                  </div>

                  <p className="mt-6 text-[10px] font-bold uppercase tracking-[0.16em] text-celestial dark:text-ash">
                    {plan.code}
                  </p>

                  <h2 className="mt-1 text-2xl font-semibold">
                    {plan.name}
                  </h2>

                  <p className="mt-5 text-4xl font-semibold tracking-[-0.05em]">
                    ${price}
                    <span className="ml-1 text-sm font-medium text-deep-blue/40 dark:text-white/40">
                      {suffix}
                    </span>
                  </p>

                  <div className="mt-6 space-y-3 text-sm text-deep-blue/60 dark:text-white/55">
                    <p className="flex items-center gap-2">
                      <Check
                        size={16}
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

                    <p className="flex items-center gap-2">
                      <Check
                        size={16}
                        className="text-moss dark:text-lime-soft"
                      />
                      Full property operations workflow
                    </p>

                    <p className="flex items-center gap-2">
                      <Check
                        size={16}
                        className="text-moss dark:text-lime-soft"
                      />
                      Secure owner workspace
                    </p>
                  </div>

                  <button
                    type="button"
                    disabled={
                      loadingPlan
                      !== null
                    }
                    onClick={() =>
                      choose(plan)
                    }
                    className="mt-auto flex items-center justify-center gap-2 rounded-2xl bg-celestial px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-cyan hover:text-deep-blue disabled:opacity-50 dark:bg-moss dark:text-lime-soft"
                  >
                    {loadingPlan ===
                    plan.id
                      ? "Please wait..."
                      : plan.code ===
                        "FREE"
                        ? "Start free"
                        : "Continue to Stripe"}

                    {loadingPlan !==
                      plan.id && (
                      <ArrowRight
                        size={16}
                      />
                    )}
                  </button>
                </article>
              );
            },
          )}
        </div>
      </div>
    </main>
  );
}
