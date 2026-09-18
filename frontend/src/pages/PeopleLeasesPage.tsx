import {
  CalendarDays,
  FilterX,
  Pencil,
  Plus,
  Search,
  UserPlus,
  Users,
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
  LocationFields,
} from "../components/LocationFields";

import {
  Pagination,
} from "../components/Pagination";

import {
  ApiError,
  apiRequest,
  type FieldErrors,
} from "../lib/api";

import {
  confirmAction,
  errorAlert,
  successAlert,
} from "../lib/alerts";

import {
  loadPortfolioStructure,
} from "../lib/portfolio";

import type {
  OwnerLeaseItem,
  OwnerLeasePage,
  PropertyNode,
} from "../types/domain";

import type {
  User,
} from "../types/auth";


const EMPTY_META = {
  page: 1,
  page_size: 8,
  total: 0,
  total_pages: 0,
};


export default function PeopleLeasesPage() {
  const [
    structure,
    setStructure,
  ] = useState<PropertyNode[]>(
    [],
  );

  const [
    data,
    setData,
  ] =
    useState<OwnerLeasePage>({
      items: [],
      meta: EMPTY_META,
    });

  const [page, setPage] =
    useState(1);

  const [
    propertyId,
    setPropertyId,
  ] = useState("");

  const [
    buildingId,
    setBuildingId,
  ] = useState("");

  const [
    unitId,
    setUnitId,
  ] = useState("");

  const [
    tenantSearch,
    setTenantSearch,
  ] = useState("");

  const [
    statusFilter,
    setStatusFilter,
  ] = useState("");

  const [
    tenantModal,
    setTenantModal,
  ] = useState(false);

  const [
    leaseModal,
    setLeaseModal,
  ] = useState(false);

  const [
    editing,
    setEditing,
  ] =
    useState<
      OwnerLeaseItem | null
    >(null);


  async function loadStructure() {
    setStructure(
      await loadPortfolioStructure(),
    );
  }


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

    if (
      tenantSearch.trim()
    ) {
      params.set(
        "tenant",
        tenantSearch.trim(),
      );
    }

    if (statusFilter) {
      params.set(
        "lease_status",
        statusFilter,
      );
    }

    setData(
      await apiRequest<
        OwnerLeasePage
      >(
        `/owner/leases?${params}`,
      ),
    );
  }


  useEffect(() => {
    loadStructure();
  }, []);


  useEffect(() => {
    const timer =
      window.setTimeout(
        () => {
          load();
        },
        tenantSearch
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
    tenantSearch,
    statusFilter,
  ]);


  function resetFilters() {
    setPropertyId("");
    setBuildingId("");
    setUnitId("");
    setTenantSearch("");
    setStatusFilter("");
    setPage(1);
  }


  async function endLease(
    lease: OwnerLeaseItem,
  ) {
    const name =
      [
        lease.tenant
          .first_name,

        lease.tenant
          .last_name,
      ]
        .filter(Boolean)
        .join(" ");

    const confirmed =
      await confirmAction({
        title:
          "End this lease?",

        text:
          `${name || lease.tenant.email} will no longer have an active lease for Unit ${lease.unit_number}. Today's date will become the end date.`,

        confirmText:
          "End lease",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/leases/${lease.id}/end`,
        {
          method: "POST",
        },
      );

      await successAlert(
        "Lease ended",
        "The lease has been preserved in history.",
      );

      await load();
      await loadStructure();
    } catch (error) {
      await errorAlert(
        "Unable to end lease",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Occupancy
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            Tenants & leases
          </h1>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() =>
              setTenantModal(
                true,
              )
            }
            className="flex items-center gap-2 rounded-2xl bg-cyan px-4 py-3 text-sm font-semibold text-deep-blue dark:bg-ash dark:text-slate-green"
          >
            <UserPlus
              size={17}
            />
            New tenant
          </button>

          <button
            onClick={() =>
              setLeaseModal(
                true,
              )
            }
            className="flex items-center gap-2 rounded-2xl bg-celestial px-4 py-3 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft"
          >
            <Plus size={17} />
            New lease
          </button>
        </div>
      </div>

      {/* FILTERS */}
      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <LocationFields
            structure={structure}
            propertyId={
              propertyId
            }
            buildingId={
              buildingId
            }
            unitId={unitId}
            onPropertyChange={(
              value,
            ) => {
              setPropertyId(
                value,
              );
              setPage(1);
            }}
            onBuildingChange={(
              value,
            ) => {
              setBuildingId(
                value,
              );
              setPage(1);
            }}
            onUnitChange={(
              value,
            ) => {
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
                value={
                  tenantSearch
                }
                onChange={(
                  event,
                ) => {
                  setTenantSearch(
                    event.target
                      .value,
                  );

                  setPage(1);
                }}
                placeholder="Name or email"
                className={`${controlClass} pl-10`}
              />
            </div>
          </FormField>

          <FormField label="Status">
            <select
              value={
                statusFilter
              }
              onChange={(
                event,
              ) => {
                setStatusFilter(
                  event.target
                    .value,
                );

                setPage(1);
              }}
              className={
                controlClass
              }
            >
              <option value="">
                All statuses
              </option>

              <option value="ACTIVE">
                Active
              </option>

              <option value="ENDED">
                Ended
              </option>
            </select>
          </FormField>
        </div>

        <button
          type="button"
          onClick={
            resetFilters
          }
          className="mt-4 flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold text-celestial transition hover:bg-cyan/30 hover:text-deep-blue dark:text-ash dark:hover:bg-moss"
        >
          <FilterX size={15} />
          Clear filters
        </button>
      </section>

      {/* LEASE CARDS */}
      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        {data.items.map(
          (lease) => {
            const name =
              [
                lease.tenant
                  .first_name,

                lease.tenant
                  .last_name,
              ]
                .filter(
                  Boolean,
                )
                .join(" ");

            return (
              <article
                key={
                  lease.id
                }
                className="rounded-[1.8rem] border border-celestial/10 bg-white p-5 shadow-sm dark:border-ash/10 dark:bg-dark-card"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="flex gap-4">
                    <div className="grid size-13 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                      <Users
                        size={21}
                      />
                    </div>

                    <div>
                      <h2 className="font-semibold text-deep-blue dark:text-white">
                        {name ||
                          lease
                            .tenant
                            .email}
                      </h2>

                      <p className="mt-1 text-xs text-deep-blue/45 dark:text-white/40">
                        {
                          lease
                            .tenant
                            .email
                        }
                      </p>

                      <p className="mt-1 text-xs text-deep-blue/45 dark:text-white/40">
                        {
                          lease
                            .tenant
                            .phone_number ??
                          "No phone number"
                        }
                      </p>
                    </div>
                  </div>

                  <span
                    className={[
                      "rounded-full px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em]",
                      lease.status ===
                      "ACTIVE"
                        ? "bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft"
                        : "bg-ash text-slate-green",
                    ].join(
                      " ",
                    )}
                  >
                    {
                      lease.status
                    }
                  </span>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <LeaseInfo
                    label="Home"
                    value={`${lease.property_name} · ${lease.building_name} · Unit ${lease.unit_number}`}
                  />

                  <LeaseInfo
                    label="Monthly rent"
                    value={String(
                      lease.rent_amount,
                    )}
                  />

                  <LeaseInfo
                    label="Dates"
                    value={`${lease.start_date} → ${lease.end_date ?? "Current"}`}
                  />
                </div>

                {lease.status ===
                  "ACTIVE" && (
                  <div className="mt-5 flex gap-2 border-t border-celestial/8 pt-4 dark:border-ash/8">
                    <button
                      onClick={() =>
                        setEditing(
                          lease,
                        )
                      }
                      className="flex items-center gap-2 rounded-xl bg-cyan/50 px-3 py-2 text-xs font-semibold text-deep-blue dark:bg-moss dark:text-lime-soft"
                    >
                      <Pencil
                        size={14}
                      />
                      Edit
                    </button>

                    <button
                      onClick={() =>
                        endLease(
                          lease,
                        )
                      }
                      className="flex items-center gap-2 rounded-xl border border-red-200 px-3 py-2 text-xs font-semibold text-red-600 dark:border-red-900/50 dark:text-red-300"
                    >
                      <CalendarDays
                        size={14}
                      />
                      End lease
                    </button>
                  </div>
                )}
              </article>
            );
          },
        )}
      </div>

      <Pagination
        meta={data.meta}
        onChange={setPage}
      />

      {tenantModal && (
        <TenantForm
          onClose={() =>
            setTenantModal(
              false,
            )
          }
          onSaved={() => {
            setTenantModal(
              false,
            );
          }}
        />
      )}

      {leaseModal && (
        <CreateLeaseForm
          structure={
            structure
          }
          onClose={() =>
            setLeaseModal(
              false,
            )
          }
          onSaved={
            async () => {
              setLeaseModal(
                false,
              );

              await load();
              await loadStructure();
            }
          }
        />
      )}

      {editing && (
        <EditLeaseForm
          lease={editing}
          onClose={() =>
            setEditing(null)
          }
          onSaved={
            async () => {
              setEditing(null);
              await load();
            }
          }
        />
      )}
    </div>
  );
}


function LeaseInfo({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl bg-light-canvas p-4 dark:bg-phthalo">
      <p className="text-[9px] font-bold uppercase tracking-[0.13em] text-deep-blue/35 dark:text-white/35">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold text-deep-blue dark:text-white">
        {value}
      </p>
    </div>
  );
}


function TenantForm({
  onClose,
  onSaved,
}: {
  onClose: () => void;
  onSaved: () => void;
}) {
  const [
    firstName,
    setFirstName,
  ] = useState("");

  const [
    lastName,
    setLastName,
  ] = useState("");

  const [
    phone,
    setPhone,
  ] = useState("");

  const [email, setEmail] =
    useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    errors,
    setErrors,
  ] =
    useState<FieldErrors>(
      {},
    );


  function validate() {
    const next:
      FieldErrors = {};

    if (!firstName.trim()) {
      next.first_name =
        "First name is required.";
    }

    if (!lastName.trim()) {
      next.last_name =
        "Last name is required.";
    }

    if (
      !phone.trim() ||
      phone.trim().length < 7
    ) {
      next.phone_number =
        "Enter a valid phone number.";
    }

    if (
      !email.includes("@")
    ) {
      next.email =
        "Enter a valid email.";
    }

    if (
      password.length < 8
    ) {
      next.password =
        "Password must be at least 8 characters.";
    }

    setErrors(next);

    return (
      Object.keys(next)
        .length === 0
    );
  }


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      await apiRequest<User>(
        "/owner/tenants",
        {
          method: "POST",

          body:
            JSON.stringify({
              first_name:
                firstName,

              last_name:
                lastName,

              phone_number:
                phone,

              email,

              password,
            }),
        },
      );

      await successAlert(
        "Tenant created",
        "The tenant can now be assigned to a lease.",
      );

      onSaved();
    } catch (error) {
      if (
        error instanceof
        ApiError
      ) {
        setErrors(
          error.fieldErrors,
        );
      }

      await errorAlert(
        "Unable to create tenant",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <Modal
      title="Create tenant"
      eyebrow="Account"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="grid gap-4 sm:grid-cols-2"
      >
        <FormField
          label="First name"
          error={
            errors.first_name
          }
        >
          <input
            value={firstName}
            onChange={(e) =>
              setFirstName(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField
          label="Last name"
          error={
            errors.last_name
          }
        >
          <input
            value={lastName}
            onChange={(e) =>
              setLastName(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField
          label="Phone number"
          error={
            errors.phone_number
          }
        >
          <input
            value={phone}
            onChange={(e) =>
              setPhone(
                e.target.value,
              )
            }
            className={
              controlClass
            }
            placeholder="+961..."
          />
        </FormField>

        <FormField
          label="Email"
          error={errors.email}
        >
          <input
            type="email"
            value={email}
            onChange={(e) =>
              setEmail(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <div className="sm:col-span-2">
          <FormField
            label="Temporary password"
            error={
              errors.password
            }
          >
            <input
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(
                  e.target.value,
                )
              }
              className={
                controlClass
              }
            />
          </FormField>
        </div>

        <button className="sm:col-span-2 rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Create tenant
        </button>
      </form>
    </Modal>
  );
}


function CreateLeaseForm({
  structure,
  onClose,
  onSaved,
}: {
  structure:
    PropertyNode[];

  onClose: () => void;
  onSaved: () => void;
}) {
  const [
    propertyId,
    setPropertyId,
  ] = useState("");

  const [
    buildingId,
    setBuildingId,
  ] = useState("");

  const [
    unitId,
    setUnitId,
  ] = useState("");

  const [
    tenantEmail,
    setTenantEmail,
  ] = useState("");

  const [
    startDate,
    setStartDate,
  ] = useState("");

  const [
    endDate,
    setEndDate,
  ] = useState("");

  const [rent, setRent] =
    useState("");

  const [
    errors,
    setErrors,
  ] =
    useState<FieldErrors>(
      {},
    );


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    const next:
      FieldErrors = {};

    if (!propertyId) {
      next.property_id =
        "Select a property.";
    }

    if (!buildingId) {
      next.building_id =
        "Select a building.";
    }

    if (!unitId) {
      next.unit_id =
        "Select a vacant unit.";
    }

    if (
      !tenantEmail.includes(
        "@",
      )
    ) {
      next.tenant_email =
        "Enter a registered tenant email.";
    }

    if (!startDate) {
      next.start_date =
        "Start date is required.";
    }

    if (
      !rent ||
      Number(rent) <= 0
    ) {
      next.rent_amount =
        "Enter a valid rent amount.";
    }

    if (
      endDate &&
      startDate &&
      endDate < startDate
    ) {
      next.end_date =
        "End date cannot be before the start date.";
    }

    setErrors(next);

    if (
      Object.keys(next)
        .length
    ) {
      return;
    }

    try {
      const tenant =
        await apiRequest<User>(
          `/owner/tenants/lookup?email=${encodeURIComponent(
            tenantEmail,
          )}`,
        );

      await apiRequest(
        `/units/${unitId}/leases`,
        {
          method: "POST",

          body:
            JSON.stringify({
              tenant_user_id:
                tenant.id,

              start_date:
                startDate,

              end_date:
                endDate ||
                null,

              rent_amount:
                Number(rent),
            }),
        },
      );

      await successAlert(
        "Lease created",
        `${tenant.first_name ?? ""} ${tenant.last_name ?? ""} is now assigned to the selected unit.`,
      );

      onSaved();
    } catch (error) {
      if (
        error instanceof
          ApiError &&
        error.status === 404
      ) {
        setErrors(
          (current) => ({
            ...current,

            tenant_email:
              "No registered tenant was found with this email.",
          }),
        );

        return;
      }

      await errorAlert(
        "Unable to create lease",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <Modal
      title="Create lease"
      eyebrow="Occupancy"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="grid gap-4 md:grid-cols-2"
      >
        <LocationFields
          structure={structure}
          propertyId={
            propertyId
          }
          buildingId={
            buildingId
          }
          unitId={unitId}
          onPropertyChange={
            setPropertyId
          }
          onBuildingChange={
            setBuildingId
          }
          onUnitChange={
            setUnitId
          }
          propertyError={
            errors.property_id
          }
          buildingError={
            errors.building_id
          }
          unitError={
            errors.unit_id
          }
          vacantOnly
        />

        <FormField
          label="Tenant email"
          error={
            errors.tenant_email
          }
          hint="The email must belong to a registered TENANT account."
        >
          <input
            type="email"
            value={
              tenantEmail
            }
            onChange={(e) =>
              setTenantEmail(
                e.target.value,
              )
            }
            className={
              controlClass
            }
            placeholder="tenant@example.com"
          />
        </FormField>

        <FormField
          label="Lease start date"
          error={
            errors.start_date
          }
        >
          <input
            type="date"
            value={startDate}
            onChange={(e) =>
              setStartDate(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField
          label="Lease end date (optional)"
          error={
            errors.end_date
          }
        >
          <input
            type="date"
            value={endDate}
            onChange={(e) =>
              setEndDate(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField
          label="Monthly rent"
          error={
            errors.rent_amount
          }
        >
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={rent}
            onChange={(e) =>
              setRent(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <button className="md:col-span-2 rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Create lease
        </button>
      </form>
    </Modal>
  );
}


function EditLeaseForm({
  lease,
  onClose,
  onSaved,
}: {
  lease: OwnerLeaseItem;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [
    startDate,
    setStartDate,
  ] = useState(
    lease.start_date,
  );

  const [
    endDate,
    setEndDate,
  ] = useState(
    lease.end_date ?? "",
  );

  const [rent, setRent] =
    useState(
      String(
        lease.rent_amount,
      ),
    );


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    try {
      await apiRequest(
        `/leases/${lease.id}`,
        {
          method: "PATCH",

          body:
            JSON.stringify({
              start_date:
                startDate,

              end_date:
                endDate ||
                null,

              rent_amount:
                Number(rent),
            }),
        },
      );

      await successAlert(
        "Lease updated",
      );

      onSaved();
    } catch (error) {
      await errorAlert(
        "Unable to update lease",
        error instanceof Error
          ? error.message
          : "Update failed.",
      );
    }
  }


  return (
    <Modal
      title="Edit active lease"
      eyebrow={`${lease.property_name} · Unit ${lease.unit_number}`}
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="grid gap-4 sm:grid-cols-2"
      >
        <FormField label="Start date">
          <input
            type="date"
            value={startDate}
            onChange={(e) =>
              setStartDate(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField label="End date">
          <input
            type="date"
            value={endDate}
            onChange={(e) =>
              setEndDate(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <div className="sm:col-span-2">
          <FormField label="Monthly rent">
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={rent}
              onChange={(e) =>
                setRent(
                  e.target.value,
                )
              }
              className={
                controlClass
              }
            />
          </FormField>
        </div>

        <button className="sm:col-span-2 rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Save lease
        </button>
      </form>
    </Modal>
  );
}