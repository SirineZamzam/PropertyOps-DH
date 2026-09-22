import {
  CreditCard,
  FilterX,
  Pencil,
  Plus,
  Search,
  Trash2,
} from "lucide-react";

import { useEffect, useState, type FormEvent } from "react";

import { useLocation, useNavigate } from "react-router";

import { useAuth } from "../contexts/AuthContext";

import { useTenantHome } from "../contexts/TenantHomeContext";

import { HomeSelector } from "../components/HomeSelector";

import { PaymentHistoryPanel } from "../components/PaymentHistoryPanel";

import { Modal } from "../components/Modal";

import { FormField, controlClass } from "../components/FormField";

import { LocationFields } from "../components/LocationFields";

import { RecordCashPaymentButton, } from "../components/RecordCashPaymentButton";

import { Pagination } from "../components/Pagination";

import { ApiError, apiRequest } from "../lib/api";

import { confirmAction, errorAlert, successAlert } from "../lib/alerts";

import { loadPortfolioStructure } from "../lib/portfolio";

import type {
  OwnerLeasePage,
  OwnerRentItem,
  OwnerRentPage,
  PropertyNode,
  TenantRentObligation,
  CheckoutSessionResponse,
} from "../types/domain";

const EMPTY_META = {
  page: 1,
  page_size: 8,
  total: 0,
  total_pages: 0,
};

export default function RentPage() {
  const { user } = useAuth();

  return user?.role === "OWNER" ? <OwnerRent /> : <TenantRent />;
}

function OwnerRent() {
  const [structure, setStructure] = useState<PropertyNode[]>([]);

  const [data, setData] = useState<OwnerRentPage>({
    items: [],
    meta: EMPTY_META,
  });

  const [page, setPage] = useState(1);

  const [propertyId, setPropertyId] = useState("");

  const [buildingId, setBuildingId] = useState("");

  const [unitId, setUnitId] = useState("");

  const [tenantSearch, setTenantSearch] = useState("");

  const [statusFilter, setStatusFilter] = useState("PENDING");

  const [createOpen, setCreateOpen] = useState(false);

  const [editing, setEditing] = useState<OwnerRentItem | null>(null);

  async function load() {
    const params = new URLSearchParams({
      page: String(page),
      page_size: "8",
    });

    if (propertyId) {
      params.set("property_id", propertyId);
    }

    if (buildingId) {
      params.set("building_id", buildingId);
    }

    if (unitId) {
      params.set("unit_id", unitId);
    }

    if (tenantSearch.trim()) {
      params.set("tenant", tenantSearch.trim());
    }

    if (statusFilter) {
      params.set("rent_status", statusFilter);
    }

    setData(
      await apiRequest<OwnerRentPage>(`/owner/rent-obligations?${params}`),
    );
  }

  useEffect(() => {
    loadPortfolioStructure().then(setStructure);
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(load, tenantSearch ? 300 : 0);

    return () => window.clearTimeout(timer);
  }, [page, propertyId, buildingId, unitId, tenantSearch, statusFilter]);

  function clearFilters() {
    setPropertyId("");
    setBuildingId("");
    setUnitId("");
    setTenantSearch("");
    setStatusFilter("");
    setPage(1);
  }

  async function remove(item: OwnerRentItem) {
    const confirmed = await confirmAction({
      title: "Delete this pending obligation?",

      text: "Only pending obligations may be deleted.",

      confirmText: "Delete obligation",
    });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(`/rent-obligations/${item.id}`, {
        method: "DELETE",
      });

      await successAlert("Obligation deleted");

      await load();
    } catch (error) {
      await errorAlert(
        "Delete failed",
        error instanceof Error ? error.message : "Request failed.",
      );
    }
  }

  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div className="flex items-end justify-between gap-5">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Rent
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            Rent obligations
          </h1>

          <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
            Pending obligations are shown first by default.
          </p>
        </div>

        <button
          onClick={() => setCreateOpen(true)}
          className="flex items-center gap-2 rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft"
        >
          <Plus size={17} />
          New obligation
        </button>
      </div>

      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
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
                value={tenantSearch}
                onChange={(e) => {
                  setTenantSearch(e.target.value);
                  setPage(1);
                }}
                placeholder="Name or email"
                className={`${controlClass} pl-10`}
              />
            </div>
          </FormField>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {[
            ["", "All"],
            ["PENDING", "Pending"],
            ["PAID", "Paid"],
            ["CANCELED", "Canceled"],
          ].map(([value, label]) => (
            <button
              key={label}
              onClick={() => {
                setStatusFilter(value);
                setPage(1);
              }}
              className={[
                "rounded-full px-4 py-2 text-xs font-semibold",
                statusFilter === value
                  ? "bg-celestial text-white dark:bg-ash dark:text-slate-green"
                  : "bg-cyan/35 text-deep-blue dark:bg-moss/50 dark:text-lime-soft",
              ].join(" ")}
            >
              {label}
            </button>
          ))}
        </div>

        <button
          onClick={clearFilters}
          className="mt-4 flex items-center gap-2 text-xs font-semibold text-celestial dark:text-ash"
        >
          <FilterX size={15} />
          Clear filters
        </button>
      </section>

      <div className="mt-6 space-y-4">
        {data.items.map((item) => {
          const name = [item.tenant.first_name, item.tenant.last_name]
            .filter(Boolean)
            .join(" ");

          return (
            <article
              key={item.id}
              className="grid gap-4 rounded-[1.7rem] border border-celestial/10 bg-white p-5 md:grid-cols-[auto_1fr_auto] md:items-center dark:border-ash/10 dark:bg-dark-card"
            >
              <div className="grid size-13 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                <CreditCard size={21} />
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-semibold text-deep-blue dark:text-white">
                    {name || item.tenant.email}
                  </h2>

                  <span className="rounded-full bg-ash/50 px-3 py-1 text-[9px] font-bold uppercase tracking-[0.12em] text-slate-green">
                    {item.status}
                  </span>
                </div>

                <p className="mt-2 text-sm text-deep-blue/48 dark:text-white/42">
                  {item.property_name} · {item.building_name} · Unit{" "}
                  {item.unit_number}
                </p>

                <p className="mt-2 text-xs text-deep-blue/40 dark:text-white/35">
                  Due {item.due_date}
                </p>
              </div>

              <div className="flex items-center gap-3">
                <p className="text-xl font-semibold text-deep-blue dark:text-white">
                  {item.amount}
                </p>

                {item.status === "PENDING" && (
                  <>
                    <RecordCashPaymentButton
                     item={item}
                      onRecorded={load}
                    />
                    <button
                      onClick={() => setEditing(item)}
                      className="grid size-9 place-items-center rounded-xl bg-cyan/45 text-deep-blue dark:bg-moss dark:text-lime-soft"
                    >
                      <Pencil size={14} />
                    </button>

                    <button
                      onClick={() => remove(item)}
                      className="grid size-9 place-items-center rounded-xl text-red-600 hover:bg-red-50 dark:text-red-300"
                    >
                      <Trash2 size={14} />
                    </button>
                  </>
                )}
              </div>
            </article>
          );
        })}
      </div>

      <Pagination meta={data.meta} onChange={setPage} />
      <PaymentHistoryPanel mode="OWNER" />

      {createOpen && (
        <CreateRentForm
          structure={structure}
          onClose={() => setCreateOpen(false)}
          onSaved={async () => {
            setCreateOpen(false);
            await load();
          }}
        />
      )}

      {editing && (
        <EditRentForm
          item={editing}
          onClose={() => setEditing(null)}
          onSaved={async () => {
            setEditing(null);
            await load();
          }}
        />
      )}
    </div>
  );
}

function CreateRentForm({
  structure,
  onClose,
  onSaved,
}: {
  structure: PropertyNode[];

  onClose: () => void;
  onSaved: () => void;
}) {
  const [propertyId, setPropertyId] = useState("");

  const [buildingId, setBuildingId] = useState("");

  const [unitId, setUnitId] = useState("");

  const [tenantEmail, setTenantEmail] = useState("");

  const [dueDate, setDueDate] = useState("");

  const [amount, setAmount] = useState("");

  const [emailError, setEmailError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();

    if (!propertyId || !buildingId || !unitId) {
      await errorAlert(
        "Select the rented unit",
        "Choose its property, building, and occupied unit.",
      );
      return;
    }

    if (!tenantEmail.includes("@")) {
      setEmailError("Enter the tenant's registered email.");
      return;
    }

    if (!dueDate || !amount || Number(amount) <= 0) {
      await errorAlert(
        "Complete the form",
        "A valid due date and positive amount are required.",
      );
      return;
    }

    try {
      // Verify tenant exists.
      await apiRequest(
        `/owner/tenants/lookup?email=${encodeURIComponent(tenantEmail)}`,
      );

      // Verify tenant really has
      // an ACTIVE lease in this unit.
      const params = new URLSearchParams({
        unit_id: unitId,
        tenant: tenantEmail,
        lease_status: "ACTIVE",
        page: "1",
        page_size: "10",
      });

      const leases = await apiRequest<OwnerLeasePage>(
        `/owner/leases?${params}`,
      );

      const lease = leases.items.find(
        (item) =>
          item.tenant.email.toLowerCase() === tenantEmail.trim().toLowerCase(),
      );

      if (!lease) {
        setEmailError(
          "This tenant does not have an active lease in the selected unit.",
        );
        return;
      }

      await apiRequest(`/leases/${lease.id}/obligations`, {
        method: "POST",

        body: JSON.stringify({
          amount: Number(amount),

          due_date: dueDate,
        }),
      });

      await successAlert("Rent obligation created");

      onSaved();
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        setEmailError("No registered tenant was found with this email.");

        return;
      }

      await errorAlert(
        "Unable to create obligation",
        error instanceof Error ? error.message : "Request failed.",
      );
    }
  }

  return (
    <Modal title="Create rent obligation" eyebrow="Rent" onClose={onClose}>
      <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
        <LocationFields
          structure={structure}
          propertyId={propertyId}
          buildingId={buildingId}
          unitId={unitId}
          onPropertyChange={setPropertyId}
          onBuildingChange={setBuildingId}
          onUnitChange={setUnitId}
          occupiedOnly
        />

        <FormField
          label="Tenant email"
          error={emailError}
          hint="Must match the tenant currently leasing the selected unit."
        >
          <input
            type="email"
            value={tenantEmail}
            onChange={(e) => {
              setTenantEmail(e.target.value);
              setEmailError("");
            }}
            className={controlClass}
          />
        </FormField>

        <FormField label="Due date">
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className={controlClass}
          />
        </FormField>

        <FormField label="Amount">
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className={controlClass}
          />
        </FormField>

        <div className="sm:col-span-2 rounded-2xl bg-cyan/35 p-4 text-xs text-deep-blue dark:bg-moss dark:text-lime-soft">
          New rent obligations start as PENDING.
        </div>

        <button className="sm:col-span-2 rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Create obligation
        </button>
      </form>
    </Modal>
  );
}

function EditRentForm({
  item,
  onClose,
  onSaved,
}: {
  item: OwnerRentItem;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [amount, setAmount] = useState(String(item.amount));

  const [dueDate, setDueDate] = useState(item.due_date);

  async function submit(event: FormEvent) {
    event.preventDefault();

    try {
      await apiRequest(`/rent-obligations/${item.id}`, {
        method: "PATCH",

        body: JSON.stringify({
          amount: Number(amount),

          due_date: dueDate,
        }),
      });

      await successAlert("Obligation updated");

      onSaved();
    } catch (error) {
      await errorAlert(
        "Update failed",
        error instanceof Error ? error.message : "Request failed.",
      );
    }
  }

  return (
    <Modal
      title="Edit pending obligation"
      eyebrow={`Unit ${item.unit_number}`}
      onClose={onClose}
    >
      <form onSubmit={submit} className="space-y-4">
        <FormField label="Amount">
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className={controlClass}
          />
        </FormField>

        <FormField label="Due date">
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className={controlClass}
          />
        </FormField>

        <button className="w-full rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Save changes
        </button>
      </form>
    </Modal>
  );
}

function TenantRent() {
  const { homes, selectedHome } = useTenantHome();

  const location = useLocation();
  const navigate = useNavigate();

  const [obligations, setObligations] = useState<TenantRentObligation[]>([]);

  const [payingId, setPayingId] = useState<number | null>(null);

  async function load() {
    if (!selectedHome) {
      setObligations([]);
      return;
    }

    try {
      const data = await apiRequest<TenantRentObligation[]>(
        `/tenant/homes/${selectedHome.lease_id}/rent-obligations`,
      );

      setObligations(
        data.filter(
         (item) =>
           item.status ===
           "PENDING",
      ),
);
    } catch {
      setObligations([]);
    }
  }

  useEffect(() => {
    load();
  }, [selectedHome?.lease_id]);

  useEffect(() => {
    const params = new URLSearchParams(location.search);

    const checkout = params.get("checkout");

    if (checkout === "success") {
      successAlert(
        "Checkout completed",
        "Your payment was submitted successfully. The verified status will update when Stripe confirmation is received.",
      );

      load();

      navigate("/app/rent", {
        replace: true,
      });
    }

    if (checkout === "cancelled") {
      errorAlert(
        "Payment cancelled",
        "No payment was completed. You can try again whenever you're ready.",
      );

      navigate("/app/rent", {
        replace: true,
      });
    }
  }, []);

  async function pay(obligationId: number) {
    setPayingId(obligationId);

    try {
      const response = await apiRequest<CheckoutSessionResponse>(
        `/tenant/rent-obligations/${obligationId}/checkout`,
        {
          method: "POST",
        },
      );

      window.location.assign(response.checkout_url);
    } catch (error) {
      setPayingId(null);

      await errorAlert(
        "Unable to start payment",
        error instanceof Error ? error.message : "Please try again.",
      );
    }
  }

  if (!homes.length) {
    return (
      <div className="mx-auto max-w-5xl page-enter">
        <p className="text-deep-blue/45 dark:text-white/40">
          No active lease found.
        </p>
      </div>
    );
  }

  if (!selectedHome) {
    return null;
  }

  return (
    <div className="mx-auto max-w-5xl page-enter">
      <HomeSelector />

      <p className="mt-7 text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
        My rent
      </p>

      <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
        Rent & payments
      </h1>

      <div className="mt-8 rounded-[2rem] bg-cyan p-7 text-deep-blue dark:bg-moss dark:text-lime-soft">
        <CreditCard size={28} />

        <p className="mt-8 text-xs font-bold uppercase tracking-[0.15em] opacity-50">
          Monthly lease rent
        </p>

        <p className="mt-2 text-4xl font-semibold">
          {selectedHome.rent_amount}
        </p>

        <p className="mt-4 text-sm opacity-60">
          {selectedHome.property_name}
          {" · "}
          {selectedHome.building_name}
          {" · Unit "}
          {selectedHome.unit_number}
        </p>
      </div>

      <section className="mt-7">
        <h2 className="text-xl font-semibold text-deep-blue dark:text-white">
          Unpaid rent
        </h2>
        <p className="mt-1 text-sm text-deep-blue/45 dark:text-white/40">
  Only unpaid rent is shown here. Completed payments are kept in your payment history below.
</p>

        <div className="mt-4 space-y-3">
          {obligations.map((item) => (
            <article
              key={item.id}
              className="flex flex-col gap-4 rounded-[1.6rem] border border-celestial/10 bg-white p-5 sm:flex-row sm:items-center sm:justify-between dark:border-ash/10 dark:bg-dark-card"
            >
              <div>
                <div className="flex items-center gap-3">
                  <p className="text-2xl font-semibold text-deep-blue dark:text-white">
                    {item.amount}
                  </p>

                  <span className="rounded-full bg-cyan px-3 py-1 text-[9px] font-bold uppercase tracking-[0.12em] text-deep-blue dark:bg-moss dark:text-lime-soft">
                    {item.status}
                  </span>
                </div>

                <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
                  Due {item.due_date}
                </p>
              </div>

              {item.status === "PENDING" && (
                <button
                  type="button"
                  disabled={payingId === item.id}
                  onClick={() => pay(item.id)}
                  className="rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan hover:text-deep-blue disabled:opacity-50 dark:bg-moss dark:text-lime-soft"
                >
                  {payingId === item.id ? "Opening Stripe..." : "Pay securely"}
                </button>
              )}
            </article>
          ))}

          {!obligations.length && (
            <div className="rounded-[1.6rem] border border-dashed border-celestial/15 bg-white p-8 text-center text-sm text-deep-blue/40 dark:border-ash/15 dark:bg-dark-card dark:text-white/35">
              No unpaid rent obligations. Paid rent appears in your payment history below.
            </div>
          )}
        </div>
      </section>
      <PaymentHistoryPanel mode="TENANT" leaseId={selectedHome.lease_id} />
    </div>
  );
}
