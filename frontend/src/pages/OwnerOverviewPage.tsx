import {
  Building2,
  DoorOpen,
  Home,
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
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  flattenUnits,
  loadPortfolioStructure,
} from "../lib/portfolio";

import { apiRequest } from "../lib/api";

import type {
  Maintenance,
  PropertyNode,
} from "../types/domain";


export default function OwnerOverviewPage() {
  const [
    structure,
    setStructure,
  ] = useState<PropertyNode[]>(
    [],
  );

  const [
    openMaintenance,
    setOpenMaintenance,
  ] = useState(0);

  const [
    loading,
    setLoading,
  ] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const portfolio =
          await loadPortfolioStructure();

        setStructure(portfolio);

        const units =
          flattenUnits(portfolio);

        const records =
          await Promise.all(
            units.map(
              (unit) =>
                apiRequest<
                  Maintenance[]
                >(
                  `/units/${unit.id}/maintenance`,
                ),
            ),
          );

        setOpenMaintenance(
          records
            .flat()
            .filter(
              (item) =>
                item.status !==
                "RESOLVED",
            ).length,
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const units =
    flattenUnits(structure);

  const occupied =
    units.filter(
      (unit) =>
        unit.status ===
        "OCCUPIED",
    ).length;

  const chartData =
    structure.map(
      (property) => ({
        name:
          property.name.length >
          12
            ? `${property.name.slice(
                0,
                12,
              )}…`
            : property.name,

        units:
          property.buildings.reduce(
            (
              total,
              building,
            ) =>
              total +
              building.units
                .length,
            0,
          ),
      }),
    );

  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
          Overview
        </p>

        <h1 className="mt-2 text-4xl font-semibold tracking-[-0.055em] text-deep-blue dark:text-white">
          Your property network
        </h1>

        <p className="mt-2 text-sm text-deep-blue/50 dark:text-white/45">
          A live view of the
          portfolio structure behind
          your operations.
        </p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric
          icon={Building2}
          label="Properties"
          value={
            loading
              ? "—"
              : String(
                  structure.length,
                )
          }
        />

        <Metric
          icon={DoorOpen}
          label="Units"
          value={
            loading
              ? "—"
              : String(units.length)
          }
        />

        <Metric
          icon={Home}
          label="Occupied"
          value={
            loading
              ? "—"
              : String(occupied)
          }
        />

        <Metric
          icon={Wrench}
          label="Active maintenance"
          value={
            loading
              ? "—"
              : String(
                  openMaintenance,
                )
          }
        />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[2rem] border border-celestial/10 bg-white p-6 shadow-sm dark:border-ash/10 dark:bg-dark-card">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-celestial dark:text-ash">
              Portfolio shape
            </p>

            <h2 className="mt-2 text-xl font-semibold text-deep-blue dark:text-white">
              Units by property
            </h2>
          </div>

          <div className="mt-7 h-[280px]">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <BarChart
                data={chartData}
              >
                <CartesianGrid
                  vertical={false}
                  stroke="var(--chart-grid)"
                />

                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fontSize: 11,
                  }}
                />

                <YAxis
                  allowDecimals={
                    false
                  }
                  axisLine={false}
                  tickLine={false}
                  width={28}
                />

                <Tooltip
                  cursor={{
                    fill:
                      "rgba(135,210,248,.12)",
                  }}
                />

                <Bar
                  dataKey="units"
                  fill="var(--chart-primary)"
                  radius={[
                    10,
                    10,
                    3,
                    3,
                  ]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="rounded-[2rem] bg-cyan p-6 text-deep-blue dark:bg-moss dark:text-lime-soft">
          <p className="text-xs font-bold uppercase tracking-[0.17em] opacity-60">
            Buildings
          </p>

          <h2 className="mt-2 text-xl font-semibold">
            Walk the portfolio
          </h2>

          <div className="mt-6 space-y-3">
            {structure
              .slice(0, 4)
              .map(
                (
                  property,
                  index,
                ) => (
                  <Link
                    key={
                      property.id
                    }
                    to={`/app/properties/${property.id}`}
                    className="group flex items-center justify-between rounded-2xl bg-white/45 p-4 transition hover:-translate-y-1 hover:bg-white/65 dark:bg-phthalo/35 dark:hover:bg-phthalo/55"
                  >
                    <div className="flex items-center gap-3">
                      <div className="grid size-10 place-items-center rounded-xl bg-white/55 dark:bg-phthalo">
                        <Building2
                          size={
                            18
                          }
                        />
                      </div>

                      <div>
                        <p className="font-semibold">
                          {
                            property.name
                          }
                        </p>

                        <p className="mt-0.5 text-xs opacity-55">
                          {
                            property
                              .buildings
                              .length
                          }{" "}
                          building
                          {property
                            .buildings
                            .length ===
                          1
                            ? ""
                            : "s"}
                        </p>
                      </div>
                    </div>

                    <span className="text-xs font-bold opacity-35">
                      {String(
                        index +
                          1,
                      ).padStart(
                        2,
                        "0",
                      )}
                    </span>
                  </Link>
                ),
              )}
          </div>
        </section>
      </div>
    </div>
  );
}


function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Home;
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