import {
  FilterX,
  Pencil,
  Plus,
  ReceiptText,
  Trash2,
} from "lucide-react";

import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

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
import { apiRequest } from "../lib/api";
import {
  confirmAction,
  errorAlert,
  successAlert,
} from "../lib/alerts";
import {
  loadPortfolioStructure,
} from "../lib/portfolio";

import type {
  OwnerExpenseItem,
  OwnerExpensePage,
  PropertyNode,
} from "../types/domain";


type ExpenseView =
  | "PROPERTY"
  | "GENERAL";


const EMPTY_META = {
  page: 1,
  page_size: 8,
  total: 0,
  total_pages: 0,
};


export default function ExpensesPage() {
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
    useState<OwnerExpensePage>({
      items: [],
      meta: EMPTY_META,
    });

  const [
    activeView,
    setActiveView,
  ] = useState<ExpenseView>(
    "PROPERTY",
  );

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
    createOpen,
    setCreateOpen,
  ] = useState(false);

  const [
    editing,
    setEditing,
  ] = useState<
    OwnerExpenseItem | null
  >(null);


  async function load() {
    const params =
      new URLSearchParams({
        page: String(page),
        page_size: "8",
        scope: activeView,
      });

    if (
      activeView ===
      "PROPERTY"
    ) {
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
    }

    setData(
      await apiRequest<
        OwnerExpensePage
      >(
        `/owner/expenses?${params}`,
      ),
    );
  }


  useEffect(() => {
    loadPortfolioStructure()
      .then(setStructure);
  }, []);


  useEffect(() => {
    void load();
  }, [
    page,
    propertyId,
    buildingId,
    unitId,
    activeView,
  ]);


  function switchView(
    view: ExpenseView,
  ) {
    setActiveView(view);
    setPage(1);
    setPropertyId("");
    setBuildingId("");
    setUnitId("");
  }


  async function remove(
    expense: OwnerExpenseItem,
  ) {
    const confirmed =
      await confirmAction({
        title:
          "Delete this expense?",
        text:
          `${expense.category} · ${expense.amount}`,
        confirmText:
          "Delete expense",
      });

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/expenses/${expense.id}`,
        {
          method: "DELETE",
        },
      );

      successAlert(
        "Expense deleted",
      );

      await load();
    } catch (error) {
      await errorAlert(
        "Delete failed",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <div className="mx-auto max-w-7xl page-enter">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Costs
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            Expenses
          </h1>

          <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
            Track both property costs and general operating expenses.
          </p>
        </div>

        <button
          onClick={() =>
            setCreateOpen(true)
          }
          className="flex items-center justify-center gap-2 rounded-2xl bg-celestial px-5 py-3 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft"
        >
          <Plus size={17} />
          Add expense
        </button>
      </div>

      <div className="mt-7 inline-flex rounded-2xl bg-cyan/35 p-1 dark:bg-moss/50">
        <button
          type="button"
          onClick={() =>
            switchView("PROPERTY")
          }
          className={[
            "rounded-xl px-5 py-2.5 text-sm font-semibold transition",
            activeView ===
            "PROPERTY"
              ? "bg-white text-deep-blue shadow-sm dark:bg-phthalo dark:text-white"
              : "text-deep-blue/55 dark:text-lime-soft/65",
          ].join(" ")}
        >
          Property expenses
        </button>

        <button
          type="button"
          onClick={() =>
            switchView("GENERAL")
          }
          className={[
            "rounded-xl px-5 py-2.5 text-sm font-semibold transition",
            activeView ===
            "GENERAL"
              ? "bg-white text-deep-blue shadow-sm dark:bg-phthalo dark:text-white"
              : "text-deep-blue/55 dark:text-lime-soft/65",
          ].join(" ")}
        >
          General expenses
        </button>
      </div>

      {activeView ===
        "PROPERTY" && (
        <section className="mt-6 rounded-[2rem] border border-celestial/10 bg-white p-5 dark:border-ash/10 dark:bg-dark-card">
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

          <button
            type="button"
            onClick={() => {
              setPropertyId("");
              setBuildingId("");
              setUnitId("");
              setPage(1);
            }}
            className="mt-4 flex items-center gap-2 text-xs font-semibold text-celestial dark:text-ash"
          >
            <FilterX size={15} />
            Clear filters
          </button>
        </section>
      )}

      {activeView ===
        "GENERAL" && (
        <div className="mt-6 rounded-[2rem] bg-cyan/35 p-5 text-sm text-deep-blue dark:bg-moss/50 dark:text-lime-soft">
          General expenses are owner-level operating costs not tied to a specific property or unit, such as software, legal, office, marketing, insurance, or administrative costs.
        </div>
      )}

      <div className="mt-6 overflow-hidden rounded-[1.8rem] border border-celestial/10 bg-white shadow-sm dark:border-ash/10 dark:bg-dark-card">
        <div className="overflow-x-auto">
          <table
            className={[
              "w-full border-collapse",
              activeView ===
              "PROPERTY"
                ? "min-w-[850px]"
                : "min-w-[650px]",
            ].join(" ")}
          >
            <thead>
              <tr className="border-b border-celestial/10 bg-cyan/20 text-left dark:border-ash/10 dark:bg-moss/45">
                <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
                  Date
                </th>

                <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
                  Category
                </th>

                {activeView ===
                  "PROPERTY" && (
                  <>
                    <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
                      Property
                    </th>

                    <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
                      Location
                    </th>
                  </>
                )}

                <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
                  Description
                </th>

                <th className="px-5 py-4 text-right text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
                  Amount
                </th>

                <th className="px-5 py-4 text-right text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody>
              {data.items.map(
                (expense) => (
                  <tr
                    key={expense.id}
                    className="border-b border-celestial/7 transition last:border-b-0 hover:bg-cyan/10 dark:border-ash/8 dark:hover:bg-moss/20"
                  >
                    <td className="whitespace-nowrap px-5 py-4 text-sm text-deep-blue/60 dark:text-white/55">
                      {
                        expense.expense_date
                      }
                    </td>

                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="grid size-9 shrink-0 place-items-center rounded-xl bg-cyan/55 text-deep-blue dark:bg-moss dark:text-lime-soft">
                          <ReceiptText
                            size={15}
                          />
                        </div>

                        <span className="font-semibold text-deep-blue dark:text-white">
                          {
                            expense.category
                          }
                        </span>
                      </div>
                    </td>

                    {activeView ===
                      "PROPERTY" && (
                      <>
                        <td className="px-5 py-4 text-sm font-medium text-deep-blue dark:text-white">
                          {
                            expense.property_name ??
                            "—"
                          }
                        </td>

                        <td className="px-5 py-4 text-sm text-deep-blue/50 dark:text-white/45">
                          {expense.unit_number
                            ? `${expense.building_name} · Unit ${expense.unit_number}`
                            : "Property level"}
                        </td>
                      </>
                    )}

                    <td className="max-w-[260px] px-5 py-4">
                      <p
                        className="truncate text-sm text-deep-blue/50 dark:text-white/45"
                        title={
                          expense.description ??
                          ""
                        }
                      >
                        {expense.description ??
                          "—"}
                      </p>
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-right text-base font-semibold text-deep-blue dark:text-white">
                      {
                        expense.amount
                      }
                    </td>

                    <td className="px-5 py-4">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          onClick={() =>
                            setEditing(
                              expense,
                            )
                          }
                          className="grid size-9 place-items-center rounded-xl bg-cyan/45 text-deep-blue transition hover:bg-cyan dark:bg-moss dark:text-lime-soft"
                          title="Edit expense"
                        >
                          <Pencil
                            size={14}
                          />
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            remove(
                              expense,
                            )
                          }
                          className="grid size-9 place-items-center rounded-xl text-red-600 transition hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-950/20"
                          title="Delete expense"
                        >
                          <Trash2
                            size={14}
                          />
                        </button>
                      </div>
                    </td>
                  </tr>
                ),
              )}

              {!data.items.length && (
                <tr>
                  <td
                    colSpan={
                      activeView ===
                      "PROPERTY"
                        ? 7
                        : 5
                    }
                    className="px-5 py-14 text-center"
                  >
                    <ReceiptText
                      size={26}
                      className="mx-auto text-celestial dark:text-ash"
                    />

                    <p className="mt-3 font-semibold text-deep-blue dark:text-white">
                      No expenses found
                    </p>

                    <p className="mt-1 text-sm text-deep-blue/40 dark:text-white/35">
                      Add an expense to start tracking this category of costs.
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Pagination
        meta={data.meta}
        onChange={setPage}
      />

      {createOpen && (
        <ExpenseForm
          structure={structure}
          defaultScope={
            activeView
          }
          onClose={() =>
            setCreateOpen(false)
          }
          onSaved={async (
            savedScope,
          ) => {
            setCreateOpen(false);
            switchView(
              savedScope,
            );
          }}
        />
      )}

      {editing && (
        <ExpenseForm
          structure={structure}
          expense={editing}
          defaultScope={
            editing.property_id
              ? "PROPERTY"
              : "GENERAL"
          }
          onClose={() =>
            setEditing(null)
          }
          onSaved={async () => {
            setEditing(null);
            await load();
          }}
        />
      )}
    </div>
  );
}


function ExpenseForm({
  structure,
  expense,
  defaultScope,
  onClose,
  onSaved,
}: {
  structure: PropertyNode[];
  expense?: OwnerExpenseItem;
  defaultScope: ExpenseView;
  onClose: () => void;
  onSaved: (
    scope: ExpenseView,
  ) => void;
}) {
  const [
    scope,
    setScope,
  ] = useState<ExpenseView>(
    defaultScope,
  );

  const [
    propertyId,
    setPropertyId,
  ] = useState(
    expense?.property_id
      ? String(
          expense.property_id,
        )
      : "",
  );

  const [
    buildingId,
    setBuildingId,
  ] = useState(
    expense?.building_id
      ? String(
          expense.building_id,
        )
      : "",
  );

  const [
    unitId,
    setUnitId,
  ] = useState(
    expense?.unit_id
      ? String(
          expense.unit_id,
        )
      : "",
  );

  const [
    category,
    setCategory,
  ] = useState(
    expense?.category ?? "",
  );

  const [
    amount,
    setAmount,
  ] = useState(
    expense
      ? String(
          expense.amount,
        )
      : "",
  );

  const [date, setDate] =
    useState(
      expense?.expense_date ??
        "",
    );

  const [
    description,
    setDescription,
  ] = useState(
    expense?.description ??
      "",
  );


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      scope === "PROPERTY" &&
      !propertyId
    ) {
      await errorAlert(
        "Property required",
        "Select the property this expense belongs to.",
      );
      return;
    }

    if (
      !category.trim() ||
      !date ||
      !amount ||
      Number(amount) <= 0
    ) {
      await errorAlert(
        "Complete the form",
        "Category, date, and a positive amount are required.",
      );
      return;
    }

    try {
      const common = {
        amount:
          Number(amount),
        category:
          category.trim(),
        expense_date:
          date,
        description:
          description.trim() ||
          null,
      };

      if (expense) {
        await apiRequest(
          `/expenses/${expense.id}`,
          {
            method: "PATCH",
            body:
              JSON.stringify({
                ...common,
                ...(
                  scope ===
                  "PROPERTY"
                    ? {
                        unit_id:
                          unitId
                            ? Number(
                                unitId,
                              )
                            : null,
                      }
                    : {}
                ),
              }),
          },
        );

        successAlert(
          "Expense updated",
        );
      } else if (
        scope === "GENERAL"
      ) {
        await apiRequest(
          "/owner/expenses/general",
          {
            method: "POST",
            body:
              JSON.stringify(
                common,
              ),
          },
        );

        successAlert(
          "General expense created",
        );
      } else {
        await apiRequest(
          `/properties/${propertyId}/expenses`,
          {
            method: "POST",
            body:
              JSON.stringify({
                ...common,
                unit_id:
                  unitId
                    ? Number(
                        unitId,
                      )
                    : null,
              }),
          },
        );

        successAlert(
          "Property expense created",
        );
      }

      onSaved(scope);
    } catch (error) {
      await errorAlert(
        "Unable to save expense",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    }
  }


  return (
    <Modal
      title={
        expense
          ? "Edit expense"
          : "Add expense"
      }
      eyebrow="Costs"
      onClose={onClose}
    >
      <form
        onSubmit={submit}
        className="grid gap-4 sm:grid-cols-2"
      >
        {!expense && (
          <div className="sm:col-span-2">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.14em] text-deep-blue/40 dark:text-white/35">
              Expense type
            </p>

            <div className="grid grid-cols-2 rounded-2xl bg-cyan/30 p-1 dark:bg-moss/50">
              <button
                type="button"
                onClick={() =>
                  setScope(
                    "PROPERTY",
                  )
                }
                className={[
                  "rounded-xl px-3 py-2.5 text-xs font-semibold transition",
                  scope ===
                  "PROPERTY"
                    ? "bg-white text-deep-blue shadow-sm dark:bg-phthalo dark:text-white"
                    : "text-deep-blue/55 dark:text-lime-soft/60",
                ].join(" ")}
              >
                Property expense
              </button>

              <button
                type="button"
                onClick={() => {
                  setScope(
                    "GENERAL",
                  );
                  setPropertyId("");
                  setBuildingId("");
                  setUnitId("");
                }}
                className={[
                  "rounded-xl px-3 py-2.5 text-xs font-semibold transition",
                  scope ===
                  "GENERAL"
                    ? "bg-white text-deep-blue shadow-sm dark:bg-phthalo dark:text-white"
                    : "text-deep-blue/55 dark:text-lime-soft/60",
                ].join(" ")}
              >
                General expense
              </button>
            </div>
          </div>
        )}

        {!expense &&
          scope ===
          "PROPERTY" && (
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
            unitOptional
          />
        )}

        {expense && (
          <div className="sm:col-span-2 rounded-2xl bg-cyan/35 p-4 text-sm text-deep-blue dark:bg-moss dark:text-lime-soft">
            {scope ===
            "GENERAL"
              ? "General owner-level expense"
              : (
                <>
                  {
                    expense.property_name
                  }
                  {expense.unit_number
                    ? ` · ${expense.building_name} · Unit ${expense.unit_number}`
                    : " · Property level"}
                </>
              )}
          </div>
        )}

        {scope ===
          "GENERAL" &&
          !expense && (
          <div className="sm:col-span-2 rounded-2xl bg-cyan/30 p-4 text-xs text-deep-blue dark:bg-moss/50 dark:text-lime-soft">
            Use this for owner-level costs that do not belong to a specific property, such as software, legal, office, marketing, insurance, or administrative costs.
          </div>
        )}

        <FormField
          label="Category"
          hint={
            scope ===
            "GENERAL"
              ? "Examples: Software, Legal, Office, Marketing, Insurance."
              : undefined
          }
        >
          <input
            required
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

        <FormField label="Amount">
          <input
            required
            min="0.01"
            step="0.01"
            type="number"
            value={amount}
            onChange={(e) =>
              setAmount(
                e.target.value,
              )
            }
            className={
              controlClass
            }
          />
        </FormField>

        <FormField label="Expense date">
          <input
            required
            type="date"
            value={date}
            onChange={(e) =>
              setDate(
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
            label="Description"
            hint="Optional note explaining the cost."
          >
            <textarea
              rows={4}
              value={description}
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
        </div>

        <button className="sm:col-span-2 rounded-2xl bg-celestial py-3.5 text-sm font-semibold text-white dark:bg-moss dark:text-lime-soft">
          {expense
            ? "Save changes"
            : "Create expense"}
        </button>
      </form>
    </Modal>
  );
}
