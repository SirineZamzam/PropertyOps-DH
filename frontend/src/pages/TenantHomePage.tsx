import {
  Building2,
  CalendarDays,
  CreditCard,
  DoorOpen,
  Home,
  Mail,
  Phone,
  UserRound,
  Wrench,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  Link,
} from "react-router";

import {
  HomeSelector,
} from "../components/HomeSelector";

import {
  useTenantHome,
} from "../contexts/TenantHomeContext";

import {
  apiRequest,
} from "../lib/api";

import type {
  Maintenance,
} from "../types/domain";


export default function TenantHomePage() {
  const {
    homes,
    selectedHome,
    loading,
  } = useTenantHome();

  const [
    maintenance,
    setMaintenance,
  ] = useState<Maintenance[]>([]);


  useEffect(() => {
    if (!selectedHome) {
      setMaintenance([]);
      return;
    }

    apiRequest<Maintenance[]>(
      `/tenant/homes/${selectedHome.lease_id}/maintenance`,
    )
      .then(setMaintenance)
      .catch(() =>
        setMaintenance([]),
      );
  }, [
    selectedHome?.lease_id,
  ]);


  const active =
    maintenance.filter(
      (item) =>
        item.status !==
        "RESOLVED",
    );


  if (loading) {
    return (
      <p className="text-deep-blue/45 dark:text-white/40">
        Loading your homes...
      </p>
    );
  }


  if (!homes.length) {
    return (
      <div className="mx-auto max-w-4xl page-enter">
        <div className="rounded-[2rem] border border-dashed border-celestial/20 bg-white p-10 text-center dark:border-ash/15 dark:bg-dark-card">
          <Home
            size={34}
            className="mx-auto text-celestial dark:text-ash"
          />

          <h1 className="mt-5 text-2xl font-semibold text-deep-blue dark:text-white">
            No active home
          </h1>

          <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
            Your account currently has no active lease.
          </p>
        </div>
      </div>
    );
  }


  if (!selectedHome) {
    return null;
  }


  const ownerName =
    [
      selectedHome.owner
        .first_name,
      selectedHome.owner
        .last_name,
    ]
      .filter(Boolean)
      .join(" ");


  return (
    <div className="mx-auto max-w-6xl page-enter">
      <HomeSelector />

      <section className="relative mt-5 overflow-hidden rounded-[2.3rem] bg-celestial p-7 text-light-slate shadow-xl shadow-celestial/12 md:p-9 dark:bg-phthalo dark:text-white">
        <div className="absolute -right-24 -top-24 size-80 rounded-full bg-cyan/30 dark:bg-moss/70" />

        <div className="relative">
          <div className="grid size-13 place-items-center rounded-2xl bg-white/18">
            <Home size={23} />
          </div>

          <p className="mt-7 text-xs font-bold uppercase tracking-[0.18em] opacity-65">
            My home
          </p>

          <h1 className="mt-3 max-w-2xl text-4xl font-semibold tracking-[-0.055em] sm:text-5xl">
            {selectedHome.property_name}
          </h1>

          <p className="mt-3 text-sm opacity-65">
            {selectedHome.building_name}
            {" · Unit "}
            {selectedHome.unit_number}
          </p>
        </div>
      </section>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <HomeInfo
          icon={Building2}
          label="Property"
          value={
            selectedHome.property_name
          }
        />

        <HomeInfo
          icon={DoorOpen}
          label="Home"
          value={`${selectedHome.building_name} · Unit ${selectedHome.unit_number}`}
        />

        <HomeInfo
          icon={CreditCard}
          label="Monthly rent"
          value={String(
            selectedHome.rent_amount,
          )}
        />

        <HomeInfo
          icon={CalendarDays}
          label="Lease"
          value={`${selectedHome.start_date} → ${selectedHome.end_date ?? "Current"}`}
        />
      </div>

      <section className="mt-6 rounded-[2rem] border border-celestial/10 bg-white p-6 dark:border-ash/10 dark:bg-dark-card">
        <div className="flex items-start gap-4">
          <div className="grid size-12 shrink-0 place-items-center rounded-2xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
            <UserRound size={20} />
          </div>

          <div className="min-w-0">
            <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-celestial dark:text-ash">
              Property owner
            </p>

            <h2 className="mt-1 text-xl font-semibold text-deep-blue dark:text-white">
              {ownerName ||
                selectedHome.owner.email}
            </h2>

            <p className="mt-1 text-sm text-deep-blue/45 dark:text-white/40">
              Contact your property owner about lease or property questions.
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          <a
            href={`mailto:${selectedHome.owner.email}`}
            className="flex items-center gap-3 rounded-2xl bg-light-canvas p-4 text-sm font-semibold text-deep-blue transition hover:bg-cyan/35 dark:bg-phthalo dark:text-white"
          >
            <Mail
              size={17}
              className="text-celestial dark:text-ash"
            />

            <span className="truncate">
              {selectedHome.owner.email}
            </span>
          </a>

          {selectedHome.owner
            .phone_number ? (
            <a
              href={`tel:${selectedHome.owner.phone_number}`}
              className="flex items-center gap-3 rounded-2xl bg-light-canvas p-4 text-sm font-semibold text-deep-blue transition hover:bg-cyan/35 dark:bg-phthalo dark:text-white"
            >
              <Phone
                size={17}
                className="text-celestial dark:text-ash"
              />

              {selectedHome.owner.phone_number}
            </a>
          ) : (
            <div className="flex items-center gap-3 rounded-2xl bg-light-canvas p-4 text-sm text-deep-blue/45 dark:bg-phthalo dark:text-white/40">
              <Phone size={17} />
              No phone number provided
            </div>
          )}
        </div>
      </section>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <Link
          to="/app/maintenance"
          className="group rounded-[2rem] bg-cyan p-6 text-deep-blue transition hover:-translate-y-2 dark:bg-moss dark:text-lime-soft"
        >
          <Wrench size={25} />

          <p className="mt-10 text-4xl font-semibold">
            {active.length}
          </p>

          <p className="mt-1 text-sm opacity-60">
            active maintenance{" "}
            {active.length === 1
              ? "request"
              : "requests"}
          </p>

          <p className="mt-8 text-sm font-semibold">
            Open maintenance
          </p>
        </Link>

        <Link
          to="/app/rent"
          className="group rounded-[2rem] bg-ash p-6 text-slate-green transition hover:-translate-y-2"
        >
          <CreditCard size={25} />

          <p className="mt-10 text-3xl font-semibold">
            {selectedHome.rent_amount}
          </p>

          <p className="mt-1 text-sm opacity-60">
            monthly lease rent
          </p>

          <p className="mt-8 text-sm font-semibold">
            Open rent & payments
          </p>
        </Link>
      </div>

      <section className="mt-6 rounded-[2rem] border border-celestial/10 bg-white p-6 dark:border-ash/10 dark:bg-dark-card">
        <h2 className="text-xl font-semibold text-deep-blue dark:text-white">
          Recent maintenance
        </h2>

        <div className="mt-5 space-y-3">
          {maintenance
            .slice(0, 3)
            .map(
              (item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-4 rounded-2xl bg-light-canvas p-4 dark:bg-phthalo"
                >
                  <div>
                    <p className="font-semibold text-deep-blue dark:text-white">
                      {item.category}
                    </p>

                    <p className="mt-1 line-clamp-1 text-xs text-deep-blue/42 dark:text-white/35">
                      {item.description}
                    </p>
                  </div>

                  <span className="shrink-0 rounded-full bg-cyan px-3 py-1 text-[9px] font-bold uppercase tracking-[0.12em] text-deep-blue dark:bg-moss dark:text-lime-soft">
                    {item.status.replace(
                      "_",
                      " ",
                    )}
                  </span>
                </div>
              ),
            )}

          {!maintenance.length && (
            <p className="text-sm text-deep-blue/40 dark:text-white/35">
              No maintenance history for this home.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}


function HomeInfo({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Home;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[1.6rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
      <div className="grid size-10 place-items-center rounded-xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
        <Icon size={18} />
      </div>

      <p className="mt-5 text-[10px] font-bold uppercase tracking-[0.15em] text-deep-blue/35 dark:text-white/35">
        {label}
      </p>

      <p className="mt-1 font-semibold text-deep-blue dark:text-white">
        {value}
      </p>
    </div>
  );
}
