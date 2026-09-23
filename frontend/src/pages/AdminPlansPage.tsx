import {
  BadgeDollarSign,
  Infinity,
  Pencil,
  Plus,
  Trash2,
} from "lucide-react";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  Modal,
} from "../components/Modal";

import {
  FormField,
  controlClass,
} from "../components/FormField";

import {
  apiRequest,
} from "../lib/api";

import {
  confirmAction,
  errorAlert,
  successAlert,
} from "../lib/alerts";

import type {
  SubscriptionPlan,
} from "../types/subscription";


const SYSTEM_CODES = new Set([
  "FREE",
  "STANDARD",
  "PRO",
]);


function money(
  value:
    | string
    | number,
) {
  return new Intl
    .NumberFormat(
      "en-US",
      {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2,
      },
    )
    .format(
      Number(value),
    );
}


export default function AdminPlansPage() {
  const [
    plans,
    setPlans,
  ] = useState<
    SubscriptionPlan[]
  >([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    createOpen,
    setCreateOpen,
  ] = useState(false);

  const [
    editing,
    setEditing,
  ] = useState<
    SubscriptionPlan | null
  >(null);


  async function load() {
    setLoading(true);

    try {
      setPlans(
        await apiRequest<
          SubscriptionPlan[]
        >(
          "/admin/plans",
        ),
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void load();
  }, []);


  async function remove(
    plan: SubscriptionPlan,
  ) {
    const confirmed =
      await confirmAction({
        title:
          `Delete ${plan.name}?`,

        text:
          "Only unused custom plans can be deleted. System or in-use plans must be deactivated instead.",

        confirmText:
          "Delete plan",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/admin/plans/${plan.id}`,
        {
          method: "DELETE",
        },
      );

      successAlert(
        "Plan deleted",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Cannot delete plan",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Administration
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.055em] text-deep-blue dark:text-white">
            Subscription plans
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-deep-blue/50 dark:text-white/45">
            Manage pricing, property limits, and whether a plan is available for new selections.
          </p>
        </div>

        <button
          type="button"
          onClick={() =>
            setCreateOpen(true)
          }
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan hover:text-deep-blue dark:bg-moss dark:text-lime-soft"
        >
          <Plus size={17} />
          New plan
        </button>
      </div>


      {loading ? (
        <p className="mt-8 text-sm text-deep-blue/45 dark:text-white/40">
          Loading plans...
        </p>
      ) : (
        <div className="mt-8 grid gap-5 lg:grid-cols-3">
          {plans.map(
            (plan) => (
              <article
                key={plan.id}
                className="flex min-h-[330px] flex-col rounded-[2rem] border border-celestial/10 bg-white p-6 shadow-sm dark:border-ash/10 dark:bg-dark-card"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="grid size-12 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                    <BadgeDollarSign
                      size={21}
                    />
                  </div>

                  <span
                    className={[
                      "rounded-full px-3 py-1 text-[9px] font-bold uppercase tracking-[0.12em]",
                      plan.is_active
                        ? "bg-moss/10 text-moss dark:bg-lime-soft/10 dark:text-lime-soft"
                        : "bg-red-50 text-red-600 dark:bg-red-400/10 dark:text-red-300",
                    ].join(" ")}
                  >
                    {plan.is_active
                      ? "Active"
                      : "Inactive"}
                  </span>
                </div>

                <p className="mt-6 text-[10px] font-bold uppercase tracking-[0.16em] text-celestial dark:text-ash">
                  {plan.code}
                </p>

                <h2 className="mt-1 text-2xl font-semibold text-deep-blue dark:text-white">
                  {plan.name}
                </h2>

                <div className="mt-5 grid grid-cols-2 gap-3">
                  <Price
                    label="Monthly"
                    value={
                      money(
                        plan.monthly_price,
                      )
                    }
                  />

                  <Price
                    label="Yearly"
                    value={
                      money(
                        plan.yearly_price,
                      )
                    }
                  />
                </div>

                <div className="mt-4 rounded-2xl bg-light-canvas p-4 dark:bg-phthalo">
                  <p className="text-xs text-deep-blue/45 dark:text-white/40">
                    Property limit
                  </p>

                  <p className="mt-1 flex items-center gap-2 font-semibold text-deep-blue dark:text-white">
                    {plan.max_properties ===
                    null ? (
                      <>
                        <Infinity
                          size={17}
                        />
                        Unlimited
                      </>
                    ) : (
                      `${plan.max_properties} properties`
                    )}
                  </p>
                </div>

                <div className="mt-auto flex gap-2 pt-6">
                  <button
                    type="button"
                    onClick={() =>
                      setEditing(
                        plan,
                      )
                    }
                    className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-cyan/45 px-3 py-2.5 text-xs font-semibold text-deep-blue transition hover:bg-cyan dark:bg-moss dark:text-lime-soft"
                  >
                    <Pencil
                      size={14}
                    />
                    Edit
                  </button>

                  {!SYSTEM_CODES.has(
                    plan.code,
                  ) && (
                    <button
                      type="button"
                      onClick={() =>
                        remove(plan)
                      }
                      className="grid size-10 place-items-center rounded-xl text-red-600 transition hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-400/10"
                      title="Delete plan"
                    >
                      <Trash2
                        size={15}
                      />
                    </button>
                  )}
                </div>
              </article>
            ),
          )}
        </div>
      )}


      {createOpen && (
        <PlanForm
          onClose={() =>
            setCreateOpen(false)
          }
          onSaved={async () => {
            setCreateOpen(false);
            await load();
          }}
        />
      )}


      {editing && (
        <PlanForm
          plan={editing}
          onClose={() =>
            setEditing(null)
          }
          onSaved={async () => {
            setEditing(null);
            await load();
          }}
        />
      )}
    </div>
  );
}


function Price({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl bg-cyan/25 p-4 dark:bg-moss/35">
      <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-deep-blue/40 dark:text-white/35">
        {label}
      </p>

      <p className="mt-1 font-semibold text-deep-blue dark:text-white">
        {value}
      </p>
    </div>
  );
}


function PlanForm({
  plan,
  onClose,
  onSaved,
}: {
  plan?: SubscriptionPlan;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [
    code,
    setCode,
  ] = useState(
    plan?.code ?? "",
  );

  const [
    name,
    setName,
  ] = useState(
    plan?.name ?? "",
  );

  const [
    monthly,
    setMonthly,
  ] = useState(
    plan
      ? String(
          plan.monthly_price,
        )
      : "",
  );

  const [
    yearly,
    setYearly,
  ] = useState(
    plan
      ? String(
          plan.yearly_price,
        )
      : "",
  );

  const [
    maxProperties,
    setMaxProperties,
  ] = useState(
    plan?.max_properties ===
    null
      ? ""
      : plan
        ? String(
            plan.max_properties,
          )
        : "",
  );

  const [
    sortOrder,
    setSortOrder,
  ] = useState(
    plan
      ? String(
          plan.sort_order,
        )
      : "40",
  );

  const [
    active,
    setActive,
  ] = useState(
    plan?.is_active ??
      true,
  );


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !name.trim() ||
      monthly === "" ||
      yearly === ""
    ) {
      await errorAlert(
        "Complete the plan",
        "Name and both price fields are required.",
      );
      return;
    }

    const payload = {
      name:
        name.trim(),

      monthly_price:
        Number(monthly),

      yearly_price:
        Number(yearly),

      max_properties:
        maxProperties
          ? Number(
              maxProperties,
            )
          : null,

      sort_order:
        Number(
          sortOrder || 0,
        ),

      is_active:
        active,
    };

    try {
      if (plan) {
        await apiRequest(
          `/admin/plans/${plan.id}`,
          {
            method: "PATCH",
            body:
              JSON.stringify(
                payload,
              ),
          },
        );

        successAlert(
          "Plan updated",
        );
      } else {
        if (!code.trim()) {
          await errorAlert(
            "Plan code required",
            "Enter a short unique code for the plan.",
          );
          return;
        }

        await apiRequest(
          "/admin/plans",
          {
            method: "POST",
            body:
              JSON.stringify({
                code:
                  code.trim(),
                ...payload,
              }),
          },
        );

        successAlert(
          "Plan created",
        );
      }

      onSaved();
    } catch (error) {
      await errorAlert(
        "Unable to save plan",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <Modal
      title={
        plan
          ? `Edit ${plan.name}`
          : "Create plan"
      }
      eyebrow="Subscriptions"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="grid gap-4 sm:grid-cols-2"
      >
        <FormField
          label="Plan code"
          hint={
            plan
              ? "Plan codes are immutable."
              : "Example: BUSINESS"
          }
        >
          <input
            value={code}
            disabled={!!plan}
            onChange={(event) =>
              setCode(
                event.target
                  .value
                  .toUpperCase(),
              )
            }
            className={`${controlClass} ${plan ? "cursor-not-allowed opacity-60" : ""}`}
          />
        </FormField>

        <FormField label="Plan name">
          <input
            value={name}
            onChange={(event) =>
              setName(
                event.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField label="Monthly price (USD)">
          <input
            type="number"
            min="0"
            step="0.01"
            value={monthly}
            onChange={(event) =>
              setMonthly(
                event.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField label="Yearly price (USD)">
          <input
            type="number"
            min="0"
            step="0.01"
            value={yearly}
            onChange={(event) =>
              setYearly(
                event.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField
          label="Max properties"
          hint="Leave blank for unlimited."
        >
          <input
            type="number"
            min="1"
            value={
              maxProperties
            }
            onChange={(event) =>
              setMaxProperties(
                event.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField label="Display order">
          <input
            type="number"
            min="0"
            value={sortOrder}
            onChange={(event) =>
              setSortOrder(
                event.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <label className="sm:col-span-2 flex items-center justify-between gap-4 rounded-2xl bg-light-canvas p-4 dark:bg-phthalo">
          <div>
            <p className="text-sm font-semibold text-deep-blue dark:text-white">
              Available for new selections
            </p>

            <p className="mt-1 text-xs text-deep-blue/45 dark:text-white/40">
              Deactivating a plan hides it from new selections. Existing subscribers keep their plan.
            </p>
          </div>

          <input
            type="checkbox"
            checked={active}
            onChange={(event) =>
              setActive(
                event.target.checked,
              )
            }
            className="size-5"
          />
        </label>

        <button className="sm:col-span-2 rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          {plan
            ? "Save plan"
            : "Create plan"}
        </button>
      </form>
    </Modal>
  );
}
