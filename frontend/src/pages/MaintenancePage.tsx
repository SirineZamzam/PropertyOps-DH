import {
  FilterX,
  Pencil,
  Plus,
  Trash2,
  Wrench,
} from "lucide-react";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import { useAuth } from "../contexts/AuthContext";
import TenantMaintenancePage from "./TenantMaintenancePage";

import { Modal } from "../components/Modal";

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
  apiRequest,
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
  MaintenanceStatus,
  OwnerMaintenanceItem,
  OwnerMaintenancePage,
  PropertyNode,
} from "../types/domain";


const EMPTY_META = {
  page: 1,
  page_size: 8,
  total: 0,
  total_pages: 0,
};


export default function MaintenancePage() {
  const { user } =
    useAuth();

  return user?.role ===
    "OWNER"
    ? <OwnerMaintenance />
    : <TenantMaintenancePage />;
}


function OwnerMaintenance() {
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
    useState<OwnerMaintenancePage>({
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
    statusFilter,
    setStatusFilter,
  ] = useState("");

  const [
    createOpen,
    setCreateOpen,
  ] = useState(false);

  const [
    editing,
    setEditing,
  ] =
    useState<
      OwnerMaintenanceItem | null
    >(null);


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

    if (statusFilter) {
      params.set(
        "maintenance_status",
        statusFilter,
      );
    } else {
      // Default = unresolved only.
      params.set(
        "resolved",
        "false",
      );
    }

    setData(
      await apiRequest<
        OwnerMaintenancePage
      >(
        `/owner/maintenance?${params}`,
      ),
    );
  }


  useEffect(() => {
    loadPortfolioStructure()
      .then(
        setStructure,
      );
  }, []);


  useEffect(() => {
    load();
  }, [
    page,
    propertyId,
    buildingId,
    unitId,
    statusFilter,
  ]);


  function clearFilters() {
    setPropertyId("");
    setBuildingId("");
    setUnitId("");
    setStatusFilter("");
    setPage(1);
  }


  async function advance(
    item:
      OwnerMaintenanceItem,
  ) {
    const next:
      | MaintenanceStatus
      | null =
      item.status === "OPEN"
        ? "ASSIGNED"
        : item.status ===
            "ASSIGNED"
          ? "IN_PROGRESS"
          : item.status ===
              "IN_PROGRESS"
            ? "RESOLVED"
            : null;

    if (!next) {
      return;
    }

    const confirmed =
      await confirmAction({
        title:
          `Move to ${next.replace(
            "_",
            " ",
          )}?`,

        text:
          "The maintenance workflow will advance to the next status.",

        confirmText:
          "Update status",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/maintenance/${item.id}/status`,
        {
          method: "PATCH",

          body:
            JSON.stringify({
              status: next,
            }),
        },
      );

      await successAlert(
        "Status updated",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Status update failed",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  async function remove(
    item:
      OwnerMaintenanceItem,
  ) {
    const confirmed =
      await confirmAction({
        title:
          "Delete this maintenance request?",

        text:
          "Only OPEN requests without linked expenses can be deleted.",

        confirmText:
          "Delete request",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/maintenance/${item.id}`,
        {
          method: "DELETE",
        },
      );

      await successAlert(
        "Request deleted",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Cannot delete request",
        error instanceof Error
          ? error.message
          : "Delete failed.",
      );
    }
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div className="flex items-end justify-between gap-5">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Operations
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            Maintenance
          </h1>

          <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
            Showing unresolved
            issues by default.
          </p>
        </div>

        <button
          onClick={() =>
            setCreateOpen(
              true,
            )
          }
          className="flex items-center gap-2 rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft"
        >
          <Plus size={17} />
          New issue
        </button>
      </div>

      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
        <div className="grid gap-4 md:grid-cols-3">
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
        </div>

        <div className="mt-5">
          <p className="mb-2 text-xs font-bold text-deep-blue/60 dark:text-lime-soft/70">
            Status
          </p>

          <div className="flex flex-wrap gap-2">
            {[
              ["", "Active"],
              [
                "OPEN",
                "Open",
              ],
              [
                "ASSIGNED",
                "Assigned",
              ],
              [
                "IN_PROGRESS",
                "In progress",
              ],
              [
                "RESOLVED",
                "Resolved",
              ],
            ].map(
              ([
                value,
                label,
              ]) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => {
                    setStatusFilter(
                      value,
                    );

                    setPage(1);
                  }}
                  className={[
                    "rounded-full px-4 py-2 text-xs font-semibold transition",
                    statusFilter ===
                    value
                      ? "bg-celestial text-white dark:bg-ash dark:text-slate-green"
                      : "bg-cyan/35 text-deep-blue hover:bg-cyan dark:bg-moss/50 dark:text-lime-soft",
                  ].join(
                    " ",
                  )}
                >
                  {label}
                </button>
              ),
            )}
          </div>
        </div>

        <button
          onClick={
            clearFilters
          }
          className="mt-5 flex items-center gap-2 text-xs font-semibold text-celestial dark:text-ash"
        >
          <FilterX size={15} />
          Clear filters
        </button>
      </section>

      <div className="mt-6 space-y-4">
        {data.items.map(
          (item) => (
            <article
              key={item.id}
              className="rounded-[1.7rem] border border-celestial/10 bg-white p-5 shadow-sm dark:border-ash/10 dark:bg-dark-card"
            >
              <div className="grid gap-4 md:grid-cols-[auto_1fr_auto] md:items-center">
                <div className="grid size-13 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                  <Wrench
                    size={21}
                  />
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-semibold text-deep-blue dark:text-white">
                      {
                        item.category
                      }
                    </h2>

                    <span className="rounded-full bg-ash/50 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.12em] text-slate-green">
                      {item.status.replace(
                        "_",
                        " ",
                      )}
                    </span>
                  </div>

                  <p className="mt-2 text-sm text-deep-blue/52 dark:text-white/45">
                    {
                      item.description
                    }
                  </p>

                  <p className="mt-3 text-xs font-medium text-celestial dark:text-ash">
                    {
                      item.property_name
                    }{" "}
                    ·{" "}
                    {
                      item.building_name
                    }{" "}
                    · Unit{" "}
                    {
                      item.unit_number
                    }
                  </p>

                  <p className="mt-1 text-xs text-deep-blue/35 dark:text-white/30">
                    Reported by{" "}
                    {[
                      item.creator
                        .first_name,
                      item.creator
                        .last_name,
                    ]
                      .filter(
                        Boolean,
                      )
                      .join(
                        " ",
                      ) ||
                      item
                        .creator
                        .email}
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  {item.status !==
                    "RESOLVED" && (
                    <>
                      <button
                        onClick={() =>
                          setEditing(
                            item,
                          )
                        }
                        className="grid size-9 place-items-center rounded-xl bg-cyan/45 text-deep-blue dark:bg-moss dark:text-lime-soft"
                        title="Edit"
                      >
                        <Pencil
                          size={15}
                        />
                      </button>

                      <button
                        onClick={() =>
                          advance(
                            item,
                          )
                        }
                        className="rounded-xl bg-celestial px-3 py-2 text-xs font-semibold text-white dark:bg-ash dark:text-slate-green"
                      >
                        {item.status ===
                        "OPEN"
                          ? "Assign"
                          : item.status ===
                              "ASSIGNED"
                            ? "Start"
                            : "Resolve"}
                      </button>
                    </>
                  )}

                  {item.status ===
                    "OPEN" && (
                    <button
                      onClick={() =>
                        remove(
                          item,
                        )
                      }
                      className="grid size-9 place-items-center rounded-xl border border-red-200 text-red-600 dark:border-red-900/50 dark:text-red-300"
                    >
                      <Trash2
                        size={15}
                      />
                    </button>
                  )}
                </div>
              </div>
            </article>
          ),
        )}
      </div>

      <Pagination
        meta={data.meta}
        onChange={setPage}
      />

      {createOpen && (
        <CreateMaintenanceForm
          structure={
            structure
          }
          onClose={() =>
            setCreateOpen(
              false,
            )
          }
          onSaved={
            async () => {
              setCreateOpen(
                false,
              );
              await load();
            }
          }
        />
      )}

      {editing && (
        <EditMaintenanceForm
          item={editing}
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


function CreateMaintenanceForm({
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
    name,
    setName,
  ] = useState("");

  const [
    description,
    setDescription,
  ] = useState("");


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !propertyId ||
      !buildingId ||
      !unitId
    ) {
      await errorAlert(
        "Select a unit",
        "Choose the property, building, and unit where the issue occurred.",
      );
      return;
    }

    if (!name.trim()) {
      await errorAlert(
        "Issue name required",
        "Give the maintenance issue a short name such as Plumbing or Electrical.",
      );
      return;
    }

    if (
      description.trim()
        .length < 5
    ) {
      await errorAlert(
        "Description too short",
        "Add enough information for the issue to be understood.",
      );
      return;
    }

    try {
      await apiRequest(
        `/units/${unitId}/maintenance`,
        {
          method: "POST",

          body:
            JSON.stringify({
              category: name,
              description,
            }),
        },
      );

      await successAlert(
        "Maintenance request created",
      );

      onSaved();
    } catch (error) {
      await errorAlert(
        "Unable to create issue",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <Modal
      title="New maintenance issue"
      eyebrow="Operations"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="grid gap-4 sm:grid-cols-2"
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
        />

        <FormField label="Issue name">
          <input
            value={name}
            onChange={(e) =>
              setName(
                e.target.value,
              )
            }
            placeholder="Plumbing"
            className={
              controlClass
            }
          />
        </FormField>

        <div className="sm:col-span-2">
          <FormField label="Description">
            <textarea
              rows={5}
              value={
                description
              }
              onChange={(e) =>
                setDescription(
                  e.target
                    .value,
                )
              }
              className={
                controlClass
              }
              placeholder="Describe what happened..."
            />
          </FormField>
        </div>

        <button className="sm:col-span-2 rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Create issue
        </button>
      </form>
    </Modal>
  );
}


function EditMaintenanceForm({
  item,
  onClose,
  onSaved,
}: {
  item:
    OwnerMaintenanceItem;

  onClose: () => void;
  onSaved: () => void;
}) {
  const [
    category,
    setCategory,
  ] = useState(
    item.category,
  );

  const [
    description,
    setDescription,
  ] = useState(
    item.description,
  );


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    try {
      await apiRequest(
        `/maintenance/${item.id}`,
        {
          method: "PATCH",

          body:
            JSON.stringify({
              category,
              description,
            }),
        },
      );

      await successAlert(
        "Maintenance updated",
      );

      onSaved();
    } catch (error) {
      await errorAlert(
        "Update failed",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <Modal
      title="Edit maintenance issue"
      eyebrow={`Unit ${item.unit_number}`}
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="space-y-4"
      >
        <FormField label="Issue name">
          <input
            value={category}
            onChange={(e) =>
              setCategory(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField label="Description">
          <textarea
            rows={5}
            value={
              description
            }
            onChange={(e) =>
              setDescription(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <button className="w-full rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Save changes
        </button>
      </form>
    </Modal>
  );
}
