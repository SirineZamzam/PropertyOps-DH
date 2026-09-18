import {
  ArrowLeft,
  BriefcaseBusiness,
  Building2,
  DoorOpen,
  Mail,
  Pencil,
  Phone,
  Plus,
  ShoppingBag,
  Trash2,
  UserRound,
  Warehouse,
} from "lucide-react";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  Link,
  useParams,
} from "react-router";

import { Modal } from "../components/Modal";

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
  Building,
  Property,
  Unit,
  UnitOccupancy,
  UnitStatus,
  UnitType,
} from "../types/domain";


interface BuildingWithUnits
  extends Building {
  units: Unit[];
}


function getUnitIcon(
  type: UnitType,
) {
  switch (type) {
    case "OFFICE":
      return BriefcaseBusiness;

    case "RETAIL":
      return ShoppingBag;

    case "STORAGE":
      return Warehouse;

    default:
      return DoorOpen;
  }
}


export default function PropertyDetailsPage() {
  const {
    propertyId,
  } = useParams();

  const id =
    Number(propertyId);

  const [
    property,
    setProperty,
  ] =
    useState<Property | null>(
      null,
    );

  const [
    buildings,
    setBuildings,
  ] = useState<
    BuildingWithUnits[]
  >([]);

  const [
    createBuilding,
    setCreateBuilding,
  ] = useState(false);

  const [
    editingBuilding,
    setEditingBuilding,
  ] =
    useState<Building | null>(
      null,
    );

  const [
    createUnitFor,
    setCreateUnitFor,
  ] =
    useState<Building | null>(
      null,
    );

  const [
    editingUnit,
    setEditingUnit,
  ] =
    useState<Unit | null>(
      null,
    );

  const [
    occupancy,
    setOccupancy,
  ] =
    useState<UnitOccupancy | null>(
      null,
    );


  async function load() {
    const properties =
      await apiRequest<
        Property[]
      >("/properties/");

    setProperty(
      properties.find(
        (item) =>
          item.id === id,
      ) ?? null,
    );

    const data =
      await apiRequest<
        Building[]
      >(
        `/properties/${id}/buildings`,
      );

    const detailed =
      await Promise.all(
        data.map(
          async (building) => ({
            ...building,

            units:
              await apiRequest<
                Unit[]
              >(
                `/buildings/${building.id}/units`,
              ),
          }),
        ),
      );

    setBuildings(
      detailed,
    );
  }


  useEffect(() => {
    if (id) {
      load();
    }
  }, [id]);


  async function deleteBuilding(
    building: Building,
  ) {
    const confirmed =
      await confirmAction({
        title:
          `Delete ${building.name}?`,

        text:
          "A building can only be deleted after all of its units have been removed.",

        confirmText:
          "Delete building",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/buildings/${building.id}`,
        {
          method: "DELETE",
        },
      );

      await successAlert(
        "Building deleted",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Cannot delete building",
        error instanceof Error
          ? error.message
          : "Delete failed.",
      );
    }
  }


  async function deleteUnit(
    unit: Unit,
  ) {
    const confirmed =
      await confirmAction({
        title:
          `Delete Unit ${unit.unit_number}?`,

        text:
          "Only vacant units without lease, maintenance, or expense history can be deleted.",

        confirmText:
          "Delete unit",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/units/${unit.id}`,
        {
          method: "DELETE",
        },
      );

      await successAlert(
        "Unit deleted",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Cannot delete unit",
        error instanceof Error
          ? error.message
          : "Delete failed.",
      );
    }
  }


  async function openUnit(
    unit: Unit,
  ) {
    if (
      unit.status !==
      "OCCUPIED"
    ) {
      setEditingUnit(unit);
      return;
    }

    try {
      const data =
        await apiRequest<
          UnitOccupancy
        >(
          `/owner/units/${unit.id}/occupancy`,
        );

      setOccupancy(data);
    } catch (error) {
      await errorAlert(
        "Unable to open unit",
        error instanceof Error
          ? error.message
          : "Could not load occupancy details.",
      );
    }
  }


  if (!property) {
    return (
      <p className="text-deep-blue/45 dark:text-white/40">
        Loading property...
      </p>
    );
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <Link
        to="/app/properties"
        className="inline-flex items-center gap-2 text-sm font-semibold text-celestial dark:text-ash"
      >
        <ArrowLeft size={16} />
        Properties
      </Link>

      <div className="mt-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Property
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            {property.name}
          </h1>

          <p className="mt-2 text-sm text-deep-blue/48 dark:text-white/42">
            {property.address},{" "}
            {property.city}
          </p>
        </div>

        <button
          onClick={() =>
            setCreateBuilding(
              true,
            )
          }
          className="flex items-center gap-2 rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft"
        >
          <Plus size={17} />
          Add building
        </button>
      </div>

      <div className="mt-8 space-y-7">
        {buildings.map(
          (building) => (
            <section
              key={building.id}
              className="overflow-hidden rounded-[2rem] border border-celestial/10 bg-white shadow-sm dark:border-ash/10 dark:bg-dark-card"
            >
              <div className="flex flex-wrap items-center justify-between gap-4 bg-cyan/60 px-6 py-5 text-deep-blue dark:bg-moss dark:text-lime-soft">
                <div className="flex items-center gap-4">
                  <div className="grid size-14 place-items-center rounded-2xl bg-white/55 dark:bg-phthalo/50">
                    <Building2
                      size={27}
                    />
                  </div>

                  <div>
                    <h2 className="text-xl font-semibold">
                      {building.name}
                    </h2>

                    <p className="mt-1 text-xs opacity-55">
                      {
                        building.units
                          .length
                      }{" "}
                      units
                    </p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() =>
                      setCreateUnitFor(
                        building,
                      )
                    }
                    className="grid size-10 place-items-center rounded-xl bg-white/50 transition hover:bg-white/80 dark:bg-phthalo/40"
                    title="Add unit"
                  >
                    <Plus
                      size={16}
                    />
                  </button>

                  <button
                    onClick={() =>
                      setEditingBuilding(
                        building,
                      )
                    }
                    className="grid size-10 place-items-center rounded-xl bg-white/50 transition hover:bg-white/80 dark:bg-phthalo/40"
                    title="Edit building"
                  >
                    <Pencil
                      size={16}
                    />
                  </button>

                  <button
                    onClick={() =>
                      deleteBuilding(
                        building,
                      )
                    }
                    className="grid size-10 place-items-center rounded-xl bg-white/50 text-red-600 transition hover:bg-red-50 dark:bg-phthalo/40 dark:text-red-300"
                    title="Delete building"
                  >
                    <Trash2
                      size={16}
                    />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 p-6 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6">
                {building.units.map(
                  (unit) => (
                    <article
                      key={unit.id}
                      className="group relative"
                    >
                      {unit.status ===
                        "VACANT" && (
                        <button
                          type="button"
                          title="Delete unit"
                          onClick={(
                            event,
                          ) => {
                            event.stopPropagation();

                            deleteUnit(
                              unit,
                            );
                          }}
                          className="absolute -right-1 -top-1 z-10 grid size-8 place-items-center rounded-full bg-white text-red-600 opacity-0 shadow-lg transition group-hover:opacity-100 dark:bg-phthalo dark:text-red-300"
                        >
                          <Trash2
                            size={13}
                          />
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() =>
                          openUnit(
                            unit,
                          )
                        }
                        className={[
                          "flex min-h-48 w-full flex-col items-center justify-center rounded-[1.7rem] p-4 text-center transition duration-300 hover:-translate-y-2 hover:shadow-lg",
                          unit.status ===
                          "OCCUPIED"
                            ? "bg-celestial text-light-slate dark:bg-moss dark:text-lime-soft"
                            : unit.status ===
                                "VACANT"
                              ? "bg-cyan text-deep-blue dark:bg-ash dark:text-slate-green"
                              : "bg-ash/60 text-slate-green dark:bg-phthalo dark:text-white/50",
                        ].join(
                          " ",
                        )}
                      >
                        {(() => {
                          const UnitIcon =
                            getUnitIcon(
                              unit.unit_type,
                            );

                          return (
                            <UnitIcon
                              size={48}
                              strokeWidth={
                                1.4
                              }
                            />
                          );
                        })()}

                        <p className="mt-5 text-xl font-bold">
                          Unit{" "}
                          {
                            unit.unit_number
                          }
                        </p>

                        <p className="mt-1 text-xs font-semibold opacity-55">
                          {unit.unit_type
                            .replace("_", " ")
                            .toLowerCase()
                            .replace(
                              /^\w/,
                              (letter) =>
                                letter.toUpperCase(),
                            )}
                        </p>

                        <span className="mt-2 rounded-full bg-white/25 px-3 py-1 text-[9px] font-bold uppercase tracking-[0.14em]">
                          {
                            unit.status
                          }
                        </span>

                        <div className="mt-4 flex items-center gap-1 text-xs font-semibold opacity-55">
                          <Pencil
                            size={12}
                          />
                          {unit.status ===
                          "OCCUPIED"
                            ? "View resident"
                            : "Edit unit"}
                        </div>
                      </button>
                    </article>
                  ),
                )}
              </div>
            </section>
          ),
        )}
      </div>

      {createBuilding && (
        <BuildingForm
          propertyId={id}
          onClose={() =>
            setCreateBuilding(
              false,
            )
          }
          onSaved={
            async () => {
              setCreateBuilding(
                false,
              );
              await load();
            }
          }
        />
      )}

      {editingBuilding && (
        <BuildingForm
          propertyId={id}
          building={
            editingBuilding
          }
          onClose={() =>
            setEditingBuilding(
              null,
            )
          }
          onSaved={
            async () => {
              setEditingBuilding(
                null,
              );
              await load();
            }
          }
        />
      )}

      {createUnitFor && (
        <UnitForm
          building={
            createUnitFor
          }
          onClose={() =>
            setCreateUnitFor(
              null,
            )
          }
          onSaved={
            async () => {
              setCreateUnitFor(
                null,
              );
              await load();
            }
          }
        />
      )}

      {editingUnit && (
        <UnitForm
          unit={editingUnit}
          building={
            buildings.find(
              (item) =>
                item.id ===
                editingUnit.building_id,
            )!
          }
          onClose={() =>
            setEditingUnit(
              null,
            )
          }
          onSaved={
            async () => {
              setEditingUnit(
                null,
              );
              await load();
            }
          }
        />
      )}

      {occupancy && (
        <ResidentModal
          occupancy={
            occupancy
          }
          onClose={() =>
            setOccupancy(null)
          }
        />
      )}
    </div>
  );
}


function BuildingForm({
  propertyId,
  building,
  onClose,
  onSaved,
}: {
  propertyId: number;
  building?: Building;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [name, setName] =
    useState(
      building?.name ?? "",
    );

  const [error, setError] =
    useState("");


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!name.trim()) {
      setError(
        "Building name is required.",
      );

      return;
    }

    try {
      if (building) {
        await apiRequest(
          `/buildings/${building.id}`,
          {
            method: "PATCH",
            body:
              JSON.stringify({
                name,
              }),
          },
        );

        await successAlert(
          "Building updated",
        );
      } else {
        await apiRequest(
          `/properties/${propertyId}/buildings`,
          {
            method: "POST",
            body:
              JSON.stringify({
                name,
              }),
          },
        );

        await successAlert(
          "Building created",
        );
      }

      onSaved();
    } catch (err) {
      await errorAlert(
        "Unable to save building",
        err instanceof Error
          ? err.message
          : "Save failed.",
      );
    }
  }


  return (
    <Modal
      title={
        building
          ? "Edit building"
          : "Create building"
      }
      eyebrow="Property"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="space-y-4"
      >
        <FormField
          label="Building name"
          error={error}
        >
          <input
            value={name}
            onChange={(e) => {
              setName(
                e.target.value,
              );
              setError("");
            }}
            className={
              controlClass
            }
          />
        </FormField>

        <button className="w-full rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          {building
            ? "Save building"
            : "Create building"}
        </button>
      </form>
    </Modal>
  );
}


function UnitForm({
  building,
  unit,
  onClose,
  onSaved,
}: {
  building: Building;
  unit?: Unit;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [
    number,
    setNumber,
  ] = useState(
    unit?.unit_number ?? "",
  );

  const [
    status,
    setStatus,
  ] =
    useState<UnitStatus>(
      unit?.status ??
        "VACANT",
    );

  const [
    unitType,
    setUnitType,
  ] = useState<UnitType>(
    unit?.unit_type ??
      "APARTMENT",
  );

  const [error, setError] =
    useState("");


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!number.trim()) {
      setError(
        "Unit number is required.",
      );
      return;
    }

    try {
      if (unit) {
        await apiRequest(
          `/units/${unit.id}`,
          {
            method: "PATCH",
            body:
              JSON.stringify({
                unit_number:
                  number,

                unit_type:
                  unitType,

                status,
              }),
          },
        );

        await successAlert(
          "Unit updated",
        );
      } else {
        await apiRequest(
          `/buildings/${building.id}/units`,
          {
            method: "POST",
            body:
              JSON.stringify({
                unit_number:
                  number,

                unit_type:
                  unitType,

                status,
              }),
          },
        );

        await successAlert(
          "Unit created",
        );
      }

      onSaved();
    } catch (err) {
      await errorAlert(
        "Unable to save unit",
        err instanceof Error
          ? err.message
          : "Save failed.",
      );
    }
  }


  return (
    <Modal
      title={
        unit
          ? `Edit Unit ${unit.unit_number}`
          : `Add unit to ${building.name}`
      }
      eyebrow="Units"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="space-y-4"
      >
        <FormField
          label="Unit number"
          error={error}
        >
          <input
            value={number}
            onChange={(e) => {
              setNumber(
                e.target.value,
              );

              setError("");
            }}
            className={
              controlClass
            }
          />
        </FormField>

        <FormField label="Unit type">
          <select
            value={unitType}
            onChange={(e) =>
              setUnitType(
                e.target
                  .value as UnitType,
              )
            }
            className={
              controlClass
            }
          >
            <option value="APARTMENT">
              Apartment
            </option>

            <option value="OFFICE">
              Office
            </option>

            <option value="RETAIL">
              Retail / Store
            </option>

            <option value="STORAGE">
              Storage
            </option>

            <option value="OTHER">
              Other
            </option>
          </select>
        </FormField>

        <FormField label="Status">
          <select
            value={status}
            disabled={
              unit?.status ===
              "OCCUPIED"
            }
            onChange={(e) =>
              setStatus(
                e.target
                  .value as UnitStatus,
              )
            }
            className={
              controlClass
            }
          >
            <option value="VACANT">
              Vacant
            </option>

            <option value="UNAVAILABLE">
              Unavailable
            </option>

            {unit?.status ===
              "OCCUPIED" && (
              <option value="OCCUPIED">
                Occupied
              </option>
            )}
          </select>
        </FormField>

        <button className="w-full rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Save unit
        </button>
      </form>
    </Modal>
  );
}


function ResidentModal({
  occupancy,
  onClose,
}: {
  occupancy: UnitOccupancy;
  onClose: () => void;
}) {
  const tenant =
    occupancy.tenant;

  return (
    <Modal
      title="Current resident"
      eyebrow="Occupied unit"
      onClose={onClose}
    >
      {!tenant ? (
        <p className="text-sm text-deep-blue/50 dark:text-white/45">
          No active tenant was
          found.
        </p>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-4 rounded-2xl bg-cyan/50 p-4 text-deep-blue dark:bg-moss dark:text-lime-soft">
            <div className="grid size-12 place-items-center rounded-xl bg-white/45 dark:bg-phthalo">
              <UserRound
                size={21}
              />
            </div>

            <div>
              <p className="font-semibold">
                {tenant.first_name}{" "}
                {tenant.last_name}
              </p>

              <p className="mt-1 text-xs opacity-55">
                Current tenant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-2xl border border-celestial/10 p-4 dark:border-ash/10">
            <Mail
              size={17}
              className="text-celestial dark:text-ash"
            />

            <span className="text-sm">
              {tenant.email}
            </span>
          </div>

          <div className="flex items-center gap-3 rounded-2xl border border-celestial/10 p-4 dark:border-ash/10">
            <Phone
              size={17}
              className="text-celestial dark:text-ash"
            />

            <span className="text-sm">
              {tenant.phone_number ??
                "No phone number"}
            </span>
          </div>

          {occupancy.lease && (
            <div className="rounded-2xl bg-ash/40 p-4 text-slate-green">
              <p className="text-xs font-bold uppercase tracking-[0.14em] opacity-55">
                Monthly rent
              </p>

              <p className="mt-1 text-lg font-semibold">
                {
                  occupancy
                    .lease
                    .rent_amount
                }
              </p>
            </div>
          )}
        </div>
      )}
    </Modal>
  );
}