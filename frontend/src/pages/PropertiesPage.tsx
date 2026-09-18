import {
  Building2,
  MapPin,
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
  useNavigate,
} from "react-router";

import {
  Modal,
} from "../components/Modal";

import {
  FormField,
  controlClass,
} from "../components/FormField";

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

import type {
  Property,
} from "../types/domain";


export default function PropertiesPage() {
  const navigate =
    useNavigate();

  const [
    properties,
    setProperties,
  ] = useState<Property[]>(
    [],
  );

  const [
    createOpen,
    setCreateOpen,
  ] = useState(false);

  const [
    editing,
    setEditing,
  ] =
    useState<Property | null>(
      null,
    );


  async function load() {
    setProperties(
      await apiRequest<
        Property[]
      >("/properties/"),
    );
  }


  useEffect(() => {
    load();
  }, []);


  async function remove(
    property: Property,
  ) {
    const confirmed =
      await confirmAction({
        title:
          `Delete ${property.name}?`,

        text:
          "A property can only be deleted when it no longer contains buildings.",

        confirmText:
          "Delete property",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/properties/${property.id}`,
        {
          method: "DELETE",
        },
      );

      await successAlert(
        "Property deleted",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Cannot delete property",
        error instanceof Error
          ? error.message
          : "The property could not be deleted.",
      );
    }
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Portfolio
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            Properties
          </h1>

          <p className="mt-2 text-sm text-deep-blue/48 dark:text-white/42">
            Select a property to
            open its buildings and
            units.
          </p>
        </div>

        <button
          onClick={() =>
            setCreateOpen(true)
          }
          className="flex items-center justify-center gap-2 rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-light-slate transition hover:-translate-y-1 hover:bg-cyan hover:text-deep-blue dark:bg-moss dark:text-lime-soft dark:hover:bg-ash dark:hover:text-slate-green"
        >
          <Plus size={17} />
          Create property
        </button>
      </div>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        {properties.map(
          (
            property,
            index,
          ) => (
            <article
              key={property.id}
              className="group relative flex min-h-[330px] flex-col overflow-hidden rounded-[2.2rem] border border-celestial/10 bg-white shadow-sm transition duration-300 hover:-translate-y-2 hover:shadow-xl dark:border-ash/10 dark:bg-dark-card"
            >
              <button
                type="button"
                onClick={() =>
                  navigate(
                    `/app/properties/${property.id}`,
                  )
                }
                className="flex flex-1 flex-col items-center px-6 pt-8 text-center"
              >
                <div
                  className={[
                    "grid size-28 place-items-center rounded-[2.2rem] transition duration-300 group-hover:scale-105",
                    index % 3 ===
                    0
                      ? "bg-cyan text-deep-blue"
                      : index % 3 ===
                          1
                        ? "bg-ash text-slate-green"
                        : "bg-celestial text-light-slate",
                    "dark:bg-moss dark:text-lime-soft",
                  ].join(" ")}
                >
                  <Building2
                    size={52}
                    strokeWidth={
                      1.5
                    }
                  />
                </div>

                <h2 className="mt-6 text-2xl font-semibold tracking-[-0.04em] text-deep-blue dark:text-white">
                  {property.name}
                </h2>

                <div className="mt-3 flex items-start justify-center gap-2 text-sm text-deep-blue/48 dark:text-white/42">
                  <MapPin
                    size={16}
                    className="mt-0.5 shrink-0 text-celestial dark:text-ash"
                  />

                  <span>
                    {
                      property.address
                    }
                    ,{" "}
                    {
                      property.city
                    }
                  </span>
                </div>
              </button>

              <div className="mx-5 mb-5 mt-6 flex gap-2 border-t border-celestial/8 pt-4 dark:border-ash/10">
                <button
                  type="button"
                  onClick={() =>
                    setEditing(
                      property,
                    )
                  }
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-cyan/55 px-3 py-2.5 text-xs font-semibold text-deep-blue transition hover:bg-cyan dark:bg-moss dark:text-lime-soft"
                >
                  <Pencil
                    size={15}
                  />
                  Edit
                </button>

                <button
                  type="button"
                  onClick={() =>
                    remove(
                      property,
                    )
                  }
                  className="grid size-10 place-items-center rounded-xl border border-red-200 text-red-600 transition hover:bg-red-50 dark:border-red-900/50 dark:text-red-300 dark:hover:bg-red-950/30"
                  title="Delete property"
                >
                  <Trash2
                    size={16}
                  />
                </button>
              </div>
            </article>
          ),
        )}
      </div>

      {createOpen && (
        <PropertyForm
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
        <PropertyForm
          property={editing}
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


function PropertyForm({
  property,
  onClose,
  onSaved,
}: {
  property?: Property;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [name, setName] =
    useState(
      property?.name ?? "",
    );

  const [
    address,
    setAddress,
  ] = useState(
    property?.address ?? "",
  );

  const [city, setCity] =
    useState(
      property?.city ?? "",
    );

  const [
    country,
    setCountry,
  ] = useState(
    property?.country ??
      "Lebanon",
  );

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

    if (!name.trim()) {
      next.name =
        "Property name is required.";
    }

    if (!address.trim()) {
      next.address =
        "Address is required.";
    }

    if (!city.trim()) {
      next.city =
        "City is required.";
    }

    if (!country.trim()) {
      next.country =
        "Country is required.";
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
      if (property) {
        await apiRequest(
          `/properties/${property.id}`,
          {
            method: "PATCH",
            body:
              JSON.stringify({
                name,
                address,
                city,
                country,
              }),
          },
        );

        await successAlert(
          "Property updated",
        );
      } else {
        await apiRequest(
          "/properties/",
          {
            method: "POST",
            body:
              JSON.stringify({
                name,
                address,
                city,
                country,
              }),
          },
        );

        await successAlert(
          "Property created",
        );
      }

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
        property
          ? "Update failed"
          : "Creation failed",

        error instanceof Error
          ? error.message
          : "Unable to save property.",
      );
    }
  }


  return (
    <Modal
      title={
        property
          ? "Edit property"
          : "Create property"
      }
      eyebrow="Portfolio"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="space-y-4"
      >
        <FormField
          label="Property name"
          error={errors.name}
        >
          <input
            value={name}
            onChange={(e) =>
              setName(
                e.target.value,
              )
            }
            className={
              controlClass
            }
            placeholder="Cedar House"
          />
        </FormField>

        <FormField
          label="Address"
          error={
            errors.address
          }
        >
          <input
            value={address}
            onChange={(e) =>
              setAddress(
                e.target.value,
              )
            }
            className={
              controlClass
            }
            placeholder="12 Cedar Street"
          />
        </FormField>

        <div className="grid gap-4 sm:grid-cols-2">
          <FormField
            label="City"
            error={errors.city}
          >
            <input
              value={city}
              onChange={(e) =>
                setCity(
                  e.target.value,
                )
              }
              className={
                controlClass
              }
            />
          </FormField>

          <FormField
            label="Country"
            error={
              errors.country
            }
          >
            <input
              value={country}
              onChange={(e) =>
                setCountry(
                  e.target.value,
                )
              }
              className={
                controlClass
              }
            />
          </FormField>
        </div>

        <button className="w-full rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white transition hover:bg-cyan hover:text-deep-blue dark:bg-moss dark:text-lime-soft">
          {property
            ? "Save changes"
            : "Create property"}
        </button>
      </form>
    </Modal>
  );
}