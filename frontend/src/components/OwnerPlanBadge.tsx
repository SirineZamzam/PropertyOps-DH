import {
  BadgeDollarSign,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useLocation,
} from "react-router";

import {
  apiRequest,
} from "../lib/api";

import type {
  OwnerSubscription,
} from "../types/subscription";


export function OwnerPlanBadge({
  collapsed,
}: {
  collapsed: boolean;
}) {
  const location =
    useLocation();

  const [
    subscription,
    setSubscription,
  ] = useState<
    OwnerSubscription | null
  >(null);


  async function load() {
    try {
      setSubscription(
        await apiRequest<
          OwnerSubscription
        >(
          "/owner/subscription",
        ),
      );
    } catch {
      setSubscription(null);
    }
  }


  useEffect(() => {
    void load();
  }, [
    location.pathname,
  ]);


  useEffect(() => {
    function refresh() {
      void load();
    }

    window.addEventListener(
      "propertyops-subscription-updated",
      refresh,
    );

    return () =>
      window.removeEventListener(
        "propertyops-subscription-updated",
        refresh,
      );
  }, []);


  if (!subscription) {
    return null;
  }


  if (collapsed) {
    return (
      <Link
        to="/app/subscription"
        title={`${subscription.plan.name} plan`}
        className="mx-auto grid size-11 place-items-center rounded-2xl bg-white/10 text-white/80 transition hover:bg-cyan hover:text-deep-blue dark:hover:bg-moss dark:hover:text-lime-soft"
      >
        <BadgeDollarSign
          size={18}
        />
      </Link>
    );
  }


  const limit =
    subscription
      .effective_max_properties;

  const usage =
    limit === null
      ? `${subscription.property_count} properties`
      : `${subscription.property_count} / ${limit} properties`;


  return (
    <Link
      to="/app/subscription"
      className="block rounded-2xl border border-white/10 bg-white/8 p-4 transition hover:bg-white/12"
    >
      <div className="flex items-center gap-3">
        <div className="grid size-9 shrink-0 place-items-center rounded-xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
          <BadgeDollarSign
            size={16}
          />
        </div>

        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-white">
            {subscription.plan.name}
          </p>

          <p className="mt-0.5 text-[10px] font-bold uppercase tracking-[0.12em] text-white/45">
            {subscription.status}
          </p>
        </div>
      </div>

      <p className="mt-3 text-xs text-white/55">
        {usage}
      </p>
    </Link>
  );
}
