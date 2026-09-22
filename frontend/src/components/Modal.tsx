import {
  useEffect,
  useId,
  type MouseEvent,
  type ReactNode,
} from "react";

import {
  createPortal,
} from "react-dom";

import {
  X,
} from "lucide-react";


interface ModalProps {
  title: string;
  eyebrow?: string;
  onClose: () => void;
  children: ReactNode;
  wide?: boolean;
}


export function Modal({
  title,
  eyebrow,
  onClose,
  children,
  wide = false,
}: ModalProps) {
  const titleId = useId();

  const theme =
    localStorage.getItem(
      "propertyops_dashboard_theme",
    ) === "dark"
      ? "dark"
      : "light";


  useEffect(() => {
    const previousOverflow =
      document.body.style.overflow;

    document.body.style.overflow =
      "hidden";


    function handleKeyDown(
      event: KeyboardEvent,
    ) {
      if (event.key === "Escape") {
        onClose();
      }
    }


    window.addEventListener(
      "keydown",
      handleKeyDown,
    );


    return () => {
      document.body.style.overflow =
        previousOverflow;

      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [onClose]);


  function handleBackdropClick(
    event: MouseEvent<HTMLDivElement>,
  ) {
    if (
      event.target ===
      event.currentTarget
    ) {
      onClose();
    }
  }


  const modal = (
    <div
      data-theme={theme}
      className="
        fixed inset-0 z-[100]
        overflow-y-auto
        bg-black/45
        px-4 py-4
        backdrop-blur-sm
        sm:px-6 sm:py-6
      "
      onMouseDown={
        handleBackdropClick
      }
    >
      <div
        className="
          flex min-h-full
          items-center
          justify-center
        "
      >
        <section
          role="dialog"
          aria-modal="true"
          aria-labelledby={titleId}
          onMouseDown={(event) =>
            event.stopPropagation()
          }
          className={[
            `
              flex
              max-h-[calc(100dvh-2rem)]
              w-full
              flex-col
              overflow-hidden
              rounded-[2rem]
              border
              border-celestial/10
              bg-white
              shadow-2xl
              shadow-black/20

              dark:border-ash/10
              dark:bg-dark-card

              sm:max-h-[calc(100dvh-3rem)]
            `,
            wide
              ? "max-w-5xl"
              : "max-w-lg",
          ].join(" ")}
        >
          <header
            className="
              flex shrink-0
              items-start
              justify-between
              gap-4
              border-b
              border-celestial/10
              bg-white
              px-6 py-5

              dark:border-ash/10
              dark:bg-dark-card
            "
          >
            <div className="min-w-0">
              {eyebrow && (
                <p
                  className="
                    text-xs
                    font-bold
                    uppercase
                    tracking-[0.18em]
                    text-celestial
                    dark:text-ash
                  "
                >
                  {eyebrow}
                </p>
              )}

              <h2
                id={titleId}
                className="
                  mt-1
                  text-2xl
                  font-semibold
                  tracking-[-0.04em]
                  text-deep-blue
                  dark:text-white
                "
              >
                {title}
              </h2>
            </div>

            <button
              type="button"
              onClick={onClose}
              aria-label="Close dialog"
              className="
                grid size-10
                shrink-0
                place-items-center
                rounded-xl
                bg-cyan/40
                text-deep-blue
                transition

                hover:bg-cyan

                focus-visible:outline-none
                focus-visible:ring-4
                focus-visible:ring-cyan/30

                dark:bg-moss
                dark:text-lime-soft
                dark:hover:bg-moss/80
              "
            >
              <X size={18} />
            </button>
          </header>

          <div
            className="
              min-h-0
              flex-1
              overflow-y-auto
              overscroll-contain
              bg-white
              px-6 py-6

              dark:bg-dark-card
            "
          >
            {children}
          </div>
        </section>
      </div>
    </div>
  );


  return createPortal(
    modal,
    document.body,
  );
}


export const inputClass =
  "w-full rounded-2xl border border-celestial/15 bg-[#f7fafb] px-4 py-3 text-sm font-medium text-deep-blue outline-none transition placeholder:text-deep-blue/30 focus:border-celestial/55 focus:ring-4 focus:ring-cyan/15 dark:border-ash/12 dark:bg-phthalo dark:text-white dark:placeholder:text-white/30 dark:focus:border-ash/40";