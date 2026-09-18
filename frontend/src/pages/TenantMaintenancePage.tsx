import {
  Building2,
  Plus,
  Wrench,
} from "lucide-react";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  HomeSelector,
} from "../components/HomeSelector";

import {
  Modal,
} from "../components/Modal";

import {
  FormField,
  controlClass,
} from "../components/FormField";

import {
  useTenantHome,
} from "../contexts/TenantHomeContext";

import {
  apiRequest,
} from "../lib/api";

import {
  errorAlert,
  successAlert,
} from "../lib/alerts";

import type {
  Maintenance,
} from "../types/domain";


export default function TenantMaintenancePage() {
  const {
    selectedHome,
    homes,
    loading,
  } = useTenantHome();

  const [
    records,
    setRecords,
  ] = useState<
    Maintenance[]
  >([]);

  const [
    createOpen,
    setCreateOpen,
  ] = useState(false);


  async function load() {
    if (!selectedHome) {
      setRecords([]);
      return;
    }

    setRecords(
      await apiRequest<
        Maintenance[]
      >(
        `/tenant/homes/${selectedHome.lease_id}/maintenance`,
      ),
    );
  }


  useEffect(() => {
    load().catch(() =>
      setRecords([]),
    );
  }, [
    selectedHome?.lease_id,
  ]);


  if (loading) {
    return (
      <p className="text-deep-blue/45 dark:text-white/40">
        Loading maintenance...
      </p>
    );
  }


  if (!homes.length) {
    return (
      <div className="rounded-[2rem] bg-white p-8 text-center dark:bg-dark-card">
        <Wrench
          size={30}
          className="mx-auto text-celestial dark:text-ash"
        />

        <p className="mt-4 font-semibold text-deep-blue dark:text-white">
          No active lease
        </p>

        <p className="mt-2 text-sm text-deep-blue/40 dark:text-white/35">
          Maintenance requests
          require an active home.
        </p>
      </div>
    );
  }


  if (!selectedHome) {
    return null;
  }


  return (
    <div className="mx-auto max-w-6xl page-enter">
      <HomeSelector />

      <div className="mt-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            My home
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            Maintenance
          </h1>

          <div className="mt-3 flex items-center gap-2 text-sm text-deep-blue/45 dark:text-white/40">
            <Building2
              size={15}
            />

            {
              selectedHome.property_name
            }{" "}
            ·{" "}
            {
              selectedHome.building_name
            }{" "}
            · Unit{" "}
            {
              selectedHome.unit_number
            }
          </div>
        </div>

        <button
          type="button"
          onClick={() =>
            setCreateOpen(
              true,
            )
          }
          className="flex items-center justify-center gap-2 rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan hover:text-deep-blue dark:bg-moss dark:text-lime-soft dark:hover:bg-ash dark:hover:text-slate-green"
        >
          <Plus size={17} />
          Report issue
        </button>
      </div>

      <div className="mt-8 space-y-4">
        {records.map(
          (item) => (
            <article
              key={item.id}
              className="grid gap-4 rounded-[1.7rem] border border-celestial/10 bg-white p-5 sm:grid-cols-[auto_1fr_auto] sm:items-center dark:border-ash/10 dark:bg-dark-card"
            >
              <div className="grid size-12 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
                <Wrench
                  size={19}
                />
              </div>

              <div>
                <h2 className="font-semibold text-deep-blue dark:text-white">
                  {
                    item.category
                  }
                </h2>

                <p className="mt-1 text-sm text-deep-blue/45 dark:text-white/40">
                  {
                    item.description
                  }
                </p>

                <p className="mt-2 text-[10px] text-deep-blue/30 dark:text-white/30">
                  Created{" "}
                  {new Date(
                    item.created_at,
                  ).toLocaleDateString()}
                </p>
              </div>

              <Status
                value={
                  item.status
                }
              />
            </article>
          ),
        )}

        {!records.length && (
          <div className="rounded-[2rem] border border-dashed border-celestial/15 bg-white p-8 text-center dark:border-ash/15 dark:bg-dark-card">
            <Wrench
              size={26}
              className="mx-auto text-celestial dark:text-ash"
            />

            <p className="mt-4 font-semibold text-deep-blue dark:text-white">
              Nothing reported
            </p>

            <p className="mt-2 text-sm text-deep-blue/40 dark:text-white/35">
              This home has no
              maintenance history
              yet.
            </p>
          </div>
        )}
      </div>

      {createOpen && (
        <TenantIssueModal
          leaseId={
            selectedHome.lease_id
          }
          homeLabel={`${selectedHome.property_name} · ${selectedHome.building_name} · Unit ${selectedHome.unit_number}`}
          onClose={() =>
            setCreateOpen(
              false,
            )
          }
          onCreated={
            async () => {
              setCreateOpen(
                false,
              );

              await load();
            }
          }
        />
      )}
    </div>
  );
}


function TenantIssueModal({
  leaseId,
  homeLabel,
  onClose,
  onCreated,
}: {
  leaseId: number;
  homeLabel: string;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [
    name,
    setName,
  ] = useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    nameError,
    setNameError,
  ] = useState("");

  const [
    descriptionError,
    setDescriptionError,
  ] = useState("");


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    let valid = true;

    if (!name.trim()) {
      setNameError(
        "Issue name is required.",
      );

      valid = false;
    }

    if (
      description.trim()
        .length < 5
    ) {
      setDescriptionError(
        "Describe the issue in at least 5 characters.",
      );

      valid = false;
    }

    if (!valid) {
      return;
    }

    try {
      await apiRequest(
        `/tenant/homes/${leaseId}/maintenance`,
        {
          method: "POST",

          body:
            JSON.stringify({
              category:
                name.trim(),

              description:
                description.trim(),
            }),
        },
      );

      await successAlert(
        "Issue reported",
        "The owner can now see this request and its exact unit.",
      );

      onCreated();
    } catch (error) {
      await errorAlert(
        "Unable to report issue",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <Modal
      title="Report an issue"
      eyebrow={homeLabel}
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="space-y-4"
      >
        <FormField
          label="Issue name"
          error={nameError}
          hint="Example: Plumbing, Electrical, Door lock"
        >
          <input
            value={name}
            onChange={(e) => {
              setName(
                e.target.value,
              );

              setNameError("");
            }}
            className={
              controlClass
            }
            placeholder="Plumbing"
          />
        </FormField>

        <FormField
          label="Description"
          error={
            descriptionError
          }
        >
          <textarea
            rows={5}
            value={
              description
            }
            onChange={(e) => {
              setDescription(
                e.target.value,
              );

              setDescriptionError(
                "",
              );
            }}
            className={
              controlClass
            }
            placeholder="The kitchen sink is leaking underneath the cabinet..."
          />
        </FormField>

        <div className="rounded-2xl bg-cyan/35 p-4 text-xs leading-5 text-deep-blue dark:bg-moss dark:text-lime-soft">
          PropertyOps automatically
          sends the correct property,
          building, unit and tenant
          information with this
          request.
        </div>

        <button className="w-full rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          Submit request
        </button>
      </form>
    </Modal>
  );
}


function Status({
  value,
}: {
  value: Maintenance["status"];
}) {
  const styles = {
    OPEN:
      "bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft",

    ASSIGNED:
      "bg-celestial/18 text-celestial dark:bg-ash dark:text-slate-green",

    IN_PROGRESS:
      "bg-ash text-slate-green",

    RESOLVED:
      "bg-moss/15 text-moss dark:bg-moss dark:text-lime-soft",
  };

  return (
    <span
      className={[
        "w-fit rounded-full px-3 py-1.5 text-[9px] font-bold uppercase tracking-[0.12em]",
        styles[value],
      ].join(" ")}
    >
      {value.replace(
        "_",
        " ",
      )}
    </span>
  );
}