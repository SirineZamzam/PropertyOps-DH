import {
  Building2,
  DoorOpen,
  Home,
  Landmark,
  TrendingDown,
  TrendingUp,
  WalletCards,
  Wrench,
} from "lucide-react";

import {
  useEffect,
  useState,
  type ReactNode,
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
  FormField,
  controlClass,
} from "../components/FormField";

import {
  apiRequest,
} from "../lib/api";

import {
  flattenUnits,
  loadPortfolioStructure,
} from "../lib/portfolio";

import type {
  FinancialOverview,
  Maintenance,
  PropertyNode,
} from "../types/domain";


type Period =
  | "MONTH"
  | "30_DAYS"
  | "YEAR"
  | "CUSTOM";


function isoDate(
  value: Date,
) {
  const year =
    value.getFullYear();

  const month =
    String(
      value.getMonth() + 1,
    ).padStart(
      2,
      "0",
    );

  const day =
    String(
      value.getDate(),
    ).padStart(
      2,
      "0",
    );

  return `${year}-${month}-${day}`;
}


function periodDates(
  period: Exclude<
    Period,
    "CUSTOM"
  >,
) {
  const today = new Date();

  if (period === "MONTH") {
    return {
      start:
        isoDate(
          new Date(
            today.getFullYear(),
            today.getMonth(),
            1,
          ),
        ),
      end:
        isoDate(today),
    };
  }

  if (
    period === "30_DAYS"
  ) {
    const start =
      new Date(today);

    start.setDate(
      start.getDate() - 29,
    );

    return {
      start:
        isoDate(start),
      end:
        isoDate(today),
    };
  }

  return {
    start:
      isoDate(
        new Date(
          today.getFullYear(),
          0,
          1,
        ),
      ),
    end:
      isoDate(today),
  };
}


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

  const [
    period,
    setPeriod,
  ] = useState<Period>(
    "MONTH",
  );

  const initialDates =
    periodDates("MONTH");

  const [
    startDate,
    setStartDate,
  ] = useState(
    initialDates.start,
  );

  const [
    endDate,
    setEndDate,
  ] = useState(
    initialDates.end,
  );

  const [
    financial,
    setFinancial,
  ] = useState<
    FinancialOverview | null
  >(null);

  const [
    financeLoading,
    setFinanceLoading,
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

    void load();
  }, []);


  useEffect(() => {
    if (
      !startDate ||
      !endDate
    ) {
      return;
    }

    async function loadFinancial() {
      setFinanceLoading(true);

      try {
        const params =
          new URLSearchParams({
            start_date:
              startDate,
            end_date:
              endDate,
          });

        const result =
          await apiRequest<
            FinancialOverview
          >(
            `/owner/financial-overview?${params}`,
          );

        setFinancial(
          result,
        );
      } finally {
        setFinanceLoading(
          false,
        );
      }
    }

    void loadFinancial();
  }, [
    startDate,
    endDate,
  ]);


  function choosePeriod(
    next:
      Exclude<
        Period,
        "CUSTOM"
      >,
  ) {
    const dates =
      periodDates(next);

    setPeriod(next);
    setStartDate(
      dates.start,
    );
    setEndDate(
      dates.end,
    );
  }


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

  const financialChart =
    financial?.series.map(
      (item) => ({
        ...item,
        rent_collected:
          Number(
            item.rent_collected,
          ),
        expenses:
          Number(
            item.expenses,
          ),
      }),
    ) ?? [];


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
          Portfolio operations and financial performance in one place.
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
              : String(
                  units.length,
                )
          }
        />

        <Metric
          icon={Home}
          label="Occupied"
          value={
            loading
              ? "—"
              : String(
                  occupied,
                )
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

      <section className="mt-7 rounded-[2rem] border border-celestial/10 bg-white p-6 shadow-sm dark:border-ash/10 dark:bg-dark-card">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-celestial dark:text-ash">
              Financial overview
            </p>

            <h2 className="mt-2 text-2xl font-semibold text-deep-blue dark:text-white">
              Income, spending & outstanding rent
            </h2>

            <p className="mt-1 text-sm text-deep-blue/45 dark:text-white/40">
              Paid rent is compared with both property and general operating expenses.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <PeriodButton
              active={
                period ===
                "MONTH"
              }
              onClick={() =>
                choosePeriod(
                  "MONTH",
                )
              }
            >
              This month
            </PeriodButton>

            <PeriodButton
              active={
                period ===
                "30_DAYS"
              }
              onClick={() =>
                choosePeriod(
                  "30_DAYS",
                )
              }
            >
              Last 30 days
            </PeriodButton>

            <PeriodButton
              active={
                period ===
                "YEAR"
              }
              onClick={() =>
                choosePeriod(
                  "YEAR",
                )
              }
            >
              This year
            </PeriodButton>

            <PeriodButton
              active={
                period ===
                "CUSTOM"
              }
              onClick={() =>
                setPeriod(
                  "CUSTOM",
                )
              }
            >
              Custom
            </PeriodButton>
          </div>
        </div>

        {period ===
          "CUSTOM" && (
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:max-w-xl">
            <FormField label="From">
              <input
                type="date"
                value={
                  startDate
                }
                onChange={(
                  event,
                ) =>
                  setStartDate(
                    event.target
                      .value,
                  )
                }
                className={
                  controlClass
                }
              />
            </FormField>

            <FormField label="To">
              <input
                type="date"
                value={
                  endDate
                }
                onChange={(
                  event,
                ) =>
                  setEndDate(
                    event.target
                      .value,
                  )
                }
                className={
                  controlClass
                }
              />
            </FormField>
          </div>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <FinanceMetric
            icon={TrendingUp}
            label="Rent collected"
            value={
              financeLoading ||
              !financial
                ? "—"
                : money(
                    financial
                      .rent_collected,
                  )
            }
          />

          <FinanceMetric
            icon={TrendingDown}
            label="Expenses"
            value={
              financeLoading ||
              !financial
                ? "—"
                : money(
                    financial
                      .expenses,
                  )
            }
          />

          <FinanceMetric
            icon={WalletCards}
            label="Net cash flow"
            value={
              financeLoading ||
              !financial
                ? "—"
                : money(
                    financial
                      .net_cash_flow,
                  )
            }
          />

          <FinanceMetric
            icon={Landmark}
            label="Outstanding rent"
            value={
              financeLoading ||
              !financial
                ? "—"
                : money(
                    financial
                      .outstanding_rent,
                  )
            }
          />
        </div>

        <div className="mt-7 h-[300px]">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <BarChart
              data={
                financialChart
              }
            >
              <CartesianGrid
                vertical={false}
                stroke="var(--chart-grid)"
              />

              <XAxis
                dataKey="label"
                axisLine={false}
                tickLine={false}
                tick={{
                  fontSize: 10,
                }}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
                width={48}
                tick={{
                  fontSize: 10,
                }}
              />

              <Tooltip
                cursor={{
                  fill:
                    "rgba(135,210,248,.12)",
                }}
                formatter={(
                  value,
                ) =>
                  money(
                    Number(value),
                  )
                }
              />

              <Bar
                dataKey="rent_collected"
                name="Rent collected"
                fill="var(--chart-primary)"
                radius={[
                  8,
                  8,
                  3,
                  3,
                ]}
              />

              <Bar
                dataKey="expenses"
                name="Expenses"
                fill="var(--chart-secondary)"
                radius={[
                  8,
                  8,
                  3,
                  3,
                ]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

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
                          size={18}
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
                        index + 1,
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


function FinanceMetric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Home;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[1.6rem] bg-light-canvas p-5 dark:bg-phthalo">
      <div className="grid size-10 place-items-center rounded-xl bg-cyan text-deep-blue dark:bg-moss dark:text-lime-soft">
        <Icon size={18} />
      </div>

      <p className="mt-4 text-xs text-deep-blue/45 dark:text-white/45">
        {label}
      </p>

      <p className="mt-1 text-xl font-semibold text-deep-blue dark:text-white">
        {value}
      </p>
    </div>
  );
}


function PeriodButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "rounded-xl px-4 py-2.5 text-xs font-semibold transition",
        active
          ? "bg-celestial text-white dark:bg-ash dark:text-slate-green"
          : "bg-cyan/35 text-deep-blue dark:bg-moss/50 dark:text-lime-soft",
      ].join(" ")}
    >
      {children}
    </button>
  );
}
