import {
  Banknote,
} from "lucide-react";

import {
  type FormEvent,
  useState,
} from "react";

import {
  FormField,
  controlClass,
} from "./FormField";

import {
  Modal,
} from "./Modal";

import {
  apiRequest,
} from "../lib/api";

import {
  errorAlert,
  successAlert,
} from "../lib/alerts";

import type {
  OwnerRentItem,
} from "../types/domain";


function todayValue() {
  const now = new Date();

  const year =
    now.getFullYear();

  const month =
    String(
      now.getMonth() + 1,
    ).padStart(
      2,
      "0",
    );

  const day =
    String(
      now.getDate(),
    ).padStart(
      2,
      "0",
    );

  return `${year}-${month}-${day}`;
}


export function RecordCashPaymentButton({
  item,
  onRecorded,
}: {
  item: OwnerRentItem;
  onRecorded: () => void | Promise<void>;
}) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    paidDate,
    setPaidDate,
  ] = useState(
    todayValue(),
  );

  const [
    note,
    setNote,
  ] = useState("");

  const [
    saving,
    setSaving,
  ] = useState(false);


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setSaving(true);

    try {
      await apiRequest(
        `/owner/rent-obligations/${item.id}/record-cash`,
        {
          method: "POST",
          body:
            JSON.stringify({
              paid_date:
                paidDate,
              note:
                note.trim() ||
                null,
            }),
        },
      );

      successAlert(
        "Cash payment recorded",
        "The rent obligation is now marked as paid.",
      );

      setOpen(false);

      window.dispatchEvent(
        new Event(
          "propertyops-payment-updated",
        ),
      );

      await onRecorded();
    } catch (error) {
      await errorAlert(
        "Unable to record payment",
        error instanceof Error
          ? error.message
          : "Request failed.",
      );
    } finally {
      setSaving(false);
    }
  }


  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        title="Record cash payment"
        aria-label="Record cash payment"
        className="
          grid size-9
          place-items-center
          rounded-xl
          bg-moss/10
          text-moss
          transition
          hover:bg-moss/20

          dark:bg-lime-soft/10
          dark:text-lime-soft
        "
      >
        <Banknote size={15} />
      </button>

      {open && (
        <Modal
          title="Record cash payment"
          eyebrow={`Unit ${item.unit_number}`}
          onClose={() =>
            setOpen(false)
          }
        >
          <form
            onSubmit={submit}
            className="space-y-4"
          >
            <div
              className="
                rounded-2xl
                bg-cyan/35
                p-4
                text-sm
                text-deep-blue

                dark:bg-moss/60
                dark:text-lime-soft
              "
            >
              <p className="font-semibold">
                {item.property_name}
                {" · "}
                {item.building_name}
                {" · Unit "}
                {item.unit_number}
              </p>

              <p className="mt-1 opacity-70">
                Amount:{" "}
                {Number(
                  item.amount,
                ).toFixed(2)}
                {" · Due "}
                {item.due_date}
              </p>
            </div>

            <FormField
              label="Paid date"
              hint="The date the cash payment was received."
            >
              <input
                type="date"
                max={todayValue()}
                value={paidDate}
                onChange={(event) =>
                  setPaidDate(
                    event.target.value,
                  )
                }
                className={
                  controlClass
                }
                required
              />
            </FormField>

            <FormField
              label="Note (optional)"
              hint="For example: Received at the office."
            >
              <textarea
                rows={3}
                maxLength={500}
                value={note}
                onChange={(event) =>
                  setNote(
                    event.target.value,
                  )
                }
                className={
                  controlClass
                }
                placeholder="Optional payment note"
              />
            </FormField>

            <div
              className="
                rounded-2xl
                border
                border-amber-200
                bg-amber-50
                p-4
                text-xs
                text-amber-800

                dark:border-amber-400/15
                dark:bg-amber-400/10
                dark:text-amber-200
              "
            >
              Recording this payment will create a PAID cash payment
              and mark this rent obligation as PAID.
            </div>

            <button
              type="submit"
              disabled={saving}
              className="
                w-full rounded-2xl
                bg-celestial
                py-3.5
                text-sm
                font-semibold
                text-white
                transition
                disabled:opacity-50

                dark:bg-moss
                dark:text-lime-soft
              "
            >
              {saving
                ? "Recording..."
                : "Record cash payment"}
            </button>
          </form>
        </Modal>
      )}
    </>
  );
}
