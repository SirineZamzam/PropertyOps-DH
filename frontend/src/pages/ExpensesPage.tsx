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
  OwnerExpenseItem,
  OwnerExpensePage,
  PropertyNode,
} from "../types/domain";


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
  ] =
    useState<
      OwnerExpenseItem | null
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
  ]);


  async function remove(
    expense:
      OwnerExpenseItem,
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

      await successAlert(
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
      <div className="flex items-end justify-between gap-5">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-celestial dark:text-ash">
            Costs
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-deep-blue dark:text-white">
            Expenses
          </h1>

          <p className="mt-2 text-sm text-deep-blue/45 dark:text-white/40">
            Newest expenses appear
            first.
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
          Add expense
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

        <button
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

     <div className="mt-6 overflow-hidden rounded-[1.8rem] border border-celestial/10 bg-white shadow-sm dark:border-ash/10 dark:bg-dark-card">
  <div className="overflow-x-auto">
    <table className="w-full min-w-[850px] border-collapse">
      <thead>
        <tr className="border-b border-celestial/10 bg-cyan/20 text-left dark:border-ash/10 dark:bg-moss/45">
          <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
            Date
          </th>

          <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
            Category
          </th>

          <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
            Property
          </th>

          <th className="px-5 py-4 text-[10px] font-bold uppercase tracking-[0.14em] text-deep-blue/50 dark:text-lime-soft/65">
            Location
          </th>

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

              <td className="px-5 py-4 text-sm font-medium text-deep-blue dark:text-white">
                {
                  expense.property_name
                }
              </td>

              <td className="px-5 py-4 text-sm text-deep-blue/50 dark:text-white/45">
                {expense.unit_number
                  ? `${expense.building_name} · Unit ${expense.unit_number}`
                  : "Property level"}
              </td>

              <td className="max-w-[250px] px-5 py-4">
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
              colSpan={7}
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
                Try changing your
                filters or add a new
                expense.
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
        <ExpenseForm
          structure={
            structure
          }
          expense={editing}
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


function ExpenseForm({
  structure,
  expense,
  onClose,
  onSaved,
}: {
  structure:
    PropertyNode[];

  expense?:
    OwnerExpenseItem;

  onClose: () => void;
  onSaved: () => void;
}) {
  const [
    propertyId,
    setPropertyId,
  ] = useState(
    expense
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

    if (!propertyId) {
      await errorAlert(
        "Property required",
        "Select the property this expense belongs to.",
      );
      return;
    }

    try {
      const payload = {
        unit_id:
          unitId
            ? Number(unitId)
            : null,

        amount:
          Number(amount),

        category,

        expense_date:
          date,

        description:
          description ||
          null,
      };

      if (expense) {
        await apiRequest(
          `/expenses/${expense.id}`,
          {
            method: "PATCH",
            body:
              JSON.stringify(
                payload,
              ),
          },
        );

        await successAlert(
          "Expense updated",
        );
      } else {
        await apiRequest(
          `/properties/${propertyId}/expenses`,
          {
            method: "POST",
            body:
              JSON.stringify(
                payload,
              ),
          },
        );

        await successAlert(
          "Expense created",
        );
      }

      onSaved();
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
          <LocationFields
            structure={
              structure
            }
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
            {
              expense.property_name
            }
            {expense.unit_number
              ? ` · ${expense.building_name} · Unit ${expense.unit_number}`
              : " · Property level"}
          </div>
        )}

        <FormField label="Category">
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
          <FormField label="Description">
            <textarea
              rows={4}
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