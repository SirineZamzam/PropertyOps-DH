import {
  Building2,
  DoorOpen,
  ShieldCheck,
  UserCheck,
  UserRound,
  UserX,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  Link,
} from "react-router";

import {
  apiRequest,
} from "../lib/api";

import type {
  AdminOverview,
} from "../types/admin";


export default function AdminOverviewPage() {
  const [
    data,
    setData,
  ] = useState<
    AdminOverview | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");

      try {
        setData(
          await apiRequest<
            AdminOverview
          >(
            "/admin/overview",
          ),
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load admin overview.",
        );
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
          Administration
        </p>

        <h1 className="mt-2 text-4xl font-semibold tracking-[-0.055em] text-deep-blue dark:text-white">
          Platform overview
        </h1>

        <p className="mt-2 text-sm text-deep-blue/50 dark:text-white/45">
          Monitor owner accounts and the property portfolio across PropertyOps.
        </p>
      </div>


      {error && (
        <div className="mt-6 rounded-2xl bg-red-50 p-4 text-sm text-red-600 dark:bg-red-400/10 dark:text-red-300">
          {error}
        </div>
      )}


      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <Metric
          icon={UserRound}
          label="Total owners"
          value={
            loading || !data
              ? "—"
              : String(
                  data.total_owners,
                )
          }
        />

        <Metric
          icon={UserCheck}
          label="Active owners"
          value={
            loading || !data
              ? "—"
              : String(
                  data.active_owners,
                )
          }
        />

        <Metric
          icon={UserX}
          label="Inactive owners"
          value={
            loading || !data
              ? "—"
              : String(
                  data.inactive_owners,
                )
          }
        />

        <Metric
          icon={Building2}
          label="Properties"
          value={
            loading || !data
              ? "—"
              : String(
                  data.total_properties,
                )
          }
        />

        <Metric
          icon={DoorOpen}
          label="Units"
          value={
            loading || !data
              ? "—"
              : String(
                  data.total_units,
                )
          }
        />
      </div>


      <section className="mt-7 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-[2rem] border border-celestial/10 bg-white p-7 shadow-sm dark:border-ash/10 dark:bg-dark-card">
          <div className="grid size-12 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
            <ShieldCheck size={21} />
          </div>

          <p className="mt-6 text-xs font-bold uppercase tracking-[0.16em] text-celestial dark:text-ash">
            Owner management
          </p>

          <h2 className="mt-2 text-2xl font-semibold text-deep-blue dark:text-white">
            Review and manage owner accounts
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-deep-blue/48 dark:text-white/42">
            View owner contact information, portfolio counts, active leases, and account status. Deactivation blocks account access without deleting business records.
          </p>

          <Link
            to="/app/admin/owners"
            className="mt-6 inline-flex rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan hover:text-deep-blue dark:bg-moss dark:text-lime-soft"
          >
            Manage owners
          </Link>
        </div>

        <div className="rounded-[2rem] bg-cyan p-7 text-deep-blue dark:bg-moss dark:text-lime-soft">
          <p className="text-xs font-bold uppercase tracking-[0.16em] opacity-55">
            Admin access
          </p>

          <h2 className="mt-2 text-2xl font-semibold">
            One protected admin workspace
          </h2>

          <p className="mt-3 text-sm leading-6 opacity-65">
            Admin accounts are not created through public registration. The role is provisioned separately and all admin routes are protected server-side.
          </p>
        </div>
      </section>
    </div>
  );
}


function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon:
    typeof UserRound;

  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[1.6rem] border border-celestial/10 bg-white p-5 shadow-sm dark:border-ash/10 dark:bg-dark-card">
      <div className="grid size-11 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
        <Icon size={19} />
      </div>

      <p className="mt-5 text-xs text-deep-blue/45 dark:text-white/45">
        {label}
      </p>

      <p className="mt-1 text-2xl font-semibold text-deep-blue dark:text-white">
        {value}
      </p>
    </div>
  );
}
