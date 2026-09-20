import {
  ArrowRight,
  CircleAlert,
  LoaderCircle,
  Radar,
  ReceiptText,
  RefreshCw,
  ShieldCheck,
  Wrench,
} from "lucide-react";

import { useState } from "react";

import { apiRequest } from "../lib/api";

import type {
  AIEvidence,
  AIAnalysisJob,
  AIQualification,
} from "../types/ai";

interface AIInsightPanelProps {
  scope: "PROPERTY" | "UNIT";

  resourceId: number;

  resourceName: string;
}

function wait(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function qualificationLabel(qualification: AIQualification) {
  switch (qualification) {
    case "HIGH":
      return "SUPPORTED";

    case "MEDIUM":
      return "AMBIGUOUS";

    case "LOW":
      return "INSUFFICIENT";
  }
}

function qualificationClass(qualification: AIQualification) {
  switch (qualification) {
    case "HIGH":
      return (
        "bg-moss/10 text-moss " +
        "dark:bg-lime-soft/10 " +
        "dark:text-lime-soft"
      );

    case "MEDIUM":
      return (
        "bg-celestial/12 " +
        "text-celestial " +
        "dark:bg-cyan/10 " +
        "dark:text-cyan"
      );

    case "LOW":
      return (
        "bg-ash/30 " +
        "text-slate-green " +
        "dark:bg-white/10 " +
        "dark:text-white/60"
      );
  }
}

function formatEvidenceDate(value: string | null) {
  if (!value) {
    return "Date unavailable";
  }

  const normalized = value.includes("T") ? value : `${value}T12:00:00`;

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(normalized));
}

export function AIInsightPanel({
  scope,
  resourceId,
  resourceName,
}: AIInsightPanelProps) {
  const [job, setJob] = useState<AIAnalysisJob | null>(null);

  const [error, setError] = useState("");

  const [requesting, setRequesting] = useState(false);

  const [selectedEvidence, setSelectedEvidence] = useState<AIEvidence | null>(
    null
  );

  const isRunning =
    requesting || job?.status === "PENDING" || job?.status === "PROCESSING";

  async function pollJob(jobId: number) {
    for (let attempt = 0; attempt < 50; attempt += 1) {
      await wait(1200);

      const updated = await apiRequest<AIAnalysisJob>(
        `/owner/ai/jobs/${jobId}`
      );

      setJob(updated);

      if (updated.status === "COMPLETED" || updated.status === "FAILED") {
        return;
      }
    }

    setError(
      "The analysis is still running. " + "You can try again shortly."
    );
  }

  async function runAnalysis() {
    setError("");
    setRequesting(true);

    try {
      const path =
        scope === "PROPERTY"
          ? `/owner/ai/properties/${resourceId}/analysis`
          : `/owner/ai/units/${resourceId}/analysis`;

      const created = await apiRequest<AIAnalysisJob>(path, {
        method: "POST",
      });

      setJob(created);

      setRequesting(false);

      await pollJob(created.id);
    } catch (err) {
      setRequesting(false);

      setError(
        err instanceof Error ? err.message : "Unable to run analysis."
      );
    }
  }

  const insight = job?.insight ?? null;

  return (
    <section
      className="
        relative overflow-hidden
        rounded-[2rem]
        border
        border-celestial/15
        bg-white
        shadow-sm
        dark:border-ash/10
        dark:bg-dark-card
      "
    >
      <div
        className="
          pointer-events-none
          absolute
          -right-20
          -top-24
          size-72
          rounded-full
          border
          border-celestial/10
          dark:border-lime-soft/5
        "
      />

      <div
        className="
          pointer-events-none
          absolute
          -right-6
          -top-10
          size-44
          rounded-full
          border
          border-celestial/10
          dark:border-lime-soft/5
        "
      />

      <div className="relative p-6 sm:p-8">
        <div
          className="
            flex flex-col
            gap-6
            lg:flex-row
            lg:items-center
            lg:justify-between
          "
        >
          <div
            className="
              flex
              max-w-2xl
              gap-4
            "
          >
            <div
              className="
                grid
                size-14
                shrink-0
                place-items-center
                rounded-2xl
                bg-cyan/45
                text-deep-blue
                dark:bg-moss
                dark:text-lime-soft
              "
            >
              <Radar size={27} strokeWidth={1.7} />
            </div>

            <div>
              <div
                className="
                  flex
                  flex-wrap
                  items-center
                  gap-2
                "
              >
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
                  PropertyOps Intelligence
                </p>

                <span
                  className="
                    rounded-full
                    bg-moss/8
                    px-2.5
                    py-1
                    text-[9px]
                    font-bold
                    uppercase
                    tracking-[0.14em]
                    text-moss
                    dark:bg-lime-soft/10
                    dark:text-lime-soft
                  "
                >
                  Evidence grounded
                </span>
              </div>

              <h2
                className="
                  mt-2
                  text-2xl
                  font-semibold
                  tracking-[-0.04em]
                  text-deep-blue
                  dark:text-white
                "
              >
                {scope === "PROPERTY"
                  ? "Property intelligence"
                  : "Unit intelligence"}
              </h2>

              <p
                className="
                  mt-2
                  max-w-xl
                  text-sm
                  leading-6
                  text-deep-blue/50
                  dark:text-white/45
                "
              >
                Review recent maintenance and expense history to uncover
                recurring operational issues before they become more costly.
              </p>

              <div className="mt-3 flex flex-wrap gap-2">
                <span className="rounded-full bg-celestial/8 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] text-celestial dark:bg-cyan/10 dark:text-cyan">
                  Last 12 months
                </span>

                <span className="rounded-full bg-moss/8 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] text-moss dark:bg-lime-soft/10 dark:text-lime-soft">
                  Maintenance + expenses
                </span>
              </div>
            </div>
          </div>

          <button
            type="button"
            disabled={isRunning}
            onClick={runAnalysis}
            className="
              group
              inline-flex
              min-w-52
              items-center
              justify-center
              gap-2
              rounded-2xl
              bg-deep-blue
              px-5
              py-3.5
              text-sm
              font-semibold
              text-white
              transition
              hover:-translate-y-0.5
              hover:shadow-lg
              disabled:cursor-not-allowed
              disabled:opacity-60
              dark:bg-lime-soft
              dark:text-phthalo
            "
          >
            {isRunning ? (
              <>
                <LoaderCircle size={17} className="animate-spin" />
                Analyzing records
              </>
            ) : insight ? (
              <>
                <RefreshCw size={16} />
                Run new scan
              </>
            ) : (
              <>
                <Radar size={17} />
                {scope === "PROPERTY" ? "Run property scan" : "Run unit scan"}
                <ArrowRight
                  size={15}
                  className="
                    transition
                    group-hover:translate-x-1
                  "
                />
              </>
            )}
          </button>
        </div>

        {isRunning && (
          <div
            className="
              mt-7
              overflow-hidden
              rounded-2xl
              border
              border-celestial/10
              bg-light-canvas
              dark:border-ash/10
              dark:bg-phthalo/40
            "
          >
            <div
              className="
                h-1
                w-full
                overflow-hidden
                bg-celestial/10
              "
            >
              <div
                className="
                  h-full
                  w-1/2
                  animate-pulse
                  rounded-full
                  bg-celestial
                  dark:bg-lime-soft
                "
              />
            </div>

            <div
              className="
                flex
                items-center
                gap-4
                p-5
              "
            >
              <div
                className="
                  grid
                  size-11
                  place-items-center
                  rounded-xl
                  bg-cyan/45
                  text-deep-blue
                  dark:bg-moss
                  dark:text-lime-soft
                "
              >
                <Radar size={20} />
              </div>

              <div>
                <p
                  className="
                    text-sm
                    font-semibold
                    text-deep-blue
                    dark:text-white
                  "
                >
                  Reading operational signals
                </p>

                <p
                  className="
                    mt-1
                    text-xs
                    text-deep-blue/45
                    dark:text-white/40
                  "
                >
                  Comparing maintenance patterns and related expenses for{" "}
                  {resourceName}.
                </p>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div
            className="
              mt-7
              flex
              gap-3
              rounded-2xl
              border
              border-red-200
              bg-red-50
              p-4
              text-red-700
              dark:border-red-400/15
              dark:bg-red-400/5
              dark:text-red-200
            "
          >
            <CircleAlert size={19} className="mt-0.5 shrink-0" />

            <div>
              <p className="text-sm font-semibold">Analysis unavailable</p>

              <p className="mt-1 text-xs opacity-75">{error}</p>
            </div>
          </div>
        )}

        {job?.status === "FAILED" && (
          <div
            className="
              mt-7
              flex
              gap-3
              rounded-2xl
              border
              border-red-200
              bg-red-50
              p-4
              text-red-700
              dark:border-red-400/15
              dark:bg-red-400/5
              dark:text-red-200
            "
          >
            <CircleAlert size={19} className="mt-0.5 shrink-0" />

            <div>
              <p className="text-sm font-semibold">Scan could not complete</p>

              <p className="mt-1 text-xs opacity-75">
                {job.error_message ?? "Please try again."}
              </p>
            </div>
          </div>
        )}

        {insight && (
          <div className="mt-8">
            <div
              className="
                grid
                gap-4
                lg:grid-cols-[1.4fr_0.8fr]
              "
            >
              <article
                className="
                  rounded-[1.6rem]
                  bg-deep-blue
                  p-6
                  text-white
                  dark:bg-phthalo
                "
              >
                <div
                  className="
                    flex
                    flex-wrap
                    items-center
                    gap-3
                  "
                >
                  <span
                    className={[
                      "rounded-full px-3 py-1",
                      "text-[10px] font-bold",
                      "uppercase tracking-[0.15em]",
                      qualificationClass(insight.qualification),
                    ].join(" ")}
                  >
                    {qualificationLabel(insight.qualification)}
                  </span>

                  <div
                    className="
                      flex
                      items-center
                      gap-1.5
                      text-xs
                      text-white/45
                    "
                  >
                    <ShieldCheck size={14} />
                    Validated evidence
                  </div>
                </div>

                <p
                  className="
                    mt-5
                    text-xs
                    font-bold
                    uppercase
                    tracking-[0.15em]
                    text-cyan
                    dark:text-lime-soft
                  "
                >
                  Finding
                </p>

                <h3
                  className="
                    mt-2
                    max-w-2xl
                    text-2xl
                    font-semibold
                    leading-tight
                    tracking-[-0.035em]
                  "
                >
                  {insight.finding}
                </h3>

                <p
                  className="
                    mt-5
                    max-w-2xl
                    text-sm
                    leading-6
                    text-white/65
                  "
                >
                  {insight.explanation}
                </p>
              </article>

              <article
                className="
                  rounded-[1.6rem]
                  border
                  border-moss/10
                  bg-moss/6
                  p-6
                  dark:border-lime-soft/10
                  dark:bg-lime-soft/5
                "
              >
                <p
                  className="
                    text-xs
                    font-bold
                    uppercase
                    tracking-[0.15em]
                    text-moss
                    dark:text-lime-soft
                  "
                >
                  Recommended action
                </p>

                <p
                  className="
                    mt-3
                    text-base
                    font-medium
                    leading-7
                    text-deep-blue
                    dark:text-white
                  "
                >
                  {insight.recommendation ??
                    "Continue monitoring this area. The current evidence does not support a specific action yet."}
                </p>
              </article>
            </div>

            <div className="mt-5">
              <div
                className="
                  flex
                  items-end
                  justify-between
                  gap-4
                "
              >
                <div>
                  <p
                    className="
                      text-xs
                      font-bold
                      uppercase
                      tracking-[0.15em]
                      text-deep-blue/45
                      dark:text-white/35
                    "
                  >
                    Supporting records
                  </p>

                  <p
                    className="
                      mt-1
                      text-sm
                      text-deep-blue/50
                      dark:text-white/40
                    "
                  >
                    Every reference below was validated against PropertyOps
                    data.
                  </p>
                </div>

                <span
                  className="
                    text-xs
                    font-semibold
                    text-deep-blue/40
                    dark:text-white/35
                  "
                >
                  {insight.evidence.length} records
                </span>
              </div>

              <div
                className="
                  mt-4
                  grid
                  gap-3
                  sm:grid-cols-2
                  xl:grid-cols-3
                "
              >
                {insight.evidence.map((evidence) => {
                  const isMaintenance =
                    evidence.evidence_type === "MAINTENANCE";

                  const Icon = isMaintenance ? Wrench : ReceiptText;

                  return (
                    <button
                      key={evidence.id}
                      type="button"
                      onClick={() => setSelectedEvidence(evidence)}
                      className="
                        flex
                        w-full
                        items-center
                        gap-3
                        rounded-2xl
                        border
                        border-celestial/10
                        bg-light-canvas
                        p-4
                        text-left
                        transition
                        hover:-translate-y-0.5
                        hover:border-celestial/25
                        hover:shadow-sm
                        dark:border-ash/10
                        dark:bg-phthalo/35
                      "
                    >
                      <div
                        className="
                          grid
                          size-10
                          shrink-0
                          place-items-center
                          rounded-xl
                          bg-cyan/45
                          text-deep-blue
                          dark:bg-moss
                          dark:text-lime-soft
                        "
                      >
                        <Icon size={17} />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div
                          className="
                            flex flex-wrap
                            items-center
                            gap-x-2
                            gap-y-1
                          "
                        >
                          <p
                            className="
                              text-sm
                              font-semibold
                              text-deep-blue
                              dark:text-white
                            "
                          >
                            {evidence.category ??
                              (isMaintenance ? "Maintenance" : "Expense")}
                          </p>

                          <span
                            className="
                              text-xs
                              text-deep-blue/35
                              dark:text-white/30
                            "
                          >
                            {formatEvidenceDate(evidence.evidence_date)}
                          </span>
                        </div>

                        <p
                          className="
                            mt-1
                            line-clamp-2
                            text-xs
                            leading-5
                            text-deep-blue/45
                            dark:text-white/40
                          "
                        >
                          {evidence.description ?? "No description available."}
                        </p>

                        <div
                          className="
                            mt-2
                            flex
                            flex-wrap
                            gap-2
                          "
                        >
                          {evidence.status && (
                            <span
                              className="
                                rounded-full
                                bg-celestial/10
                                px-2.5
                                py-1
                                text-[9px]
                                font-bold
                                uppercase
                                tracking-[0.12em]
                                text-celestial
                                dark:text-cyan
                              "
                            >
                              {evidence.status.replace("_", " ")}
                            </span>
                          )}

                          {evidence.amount && (
                            <span
                              className="
                                rounded-full
                                bg-moss/10
                                px-2.5
                                py-1
                                text-[9px]
                                font-bold
                                text-moss
                                dark:text-lime-soft
                              "
                            >
                              ${Number(evidence.amount).toFixed(2)}
                            </span>
                          )}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {selectedEvidence && (
                <div
                  className="
                    mt-4
                    rounded-[1.5rem]
                    border
                    border-celestial/12
                    bg-cyan/15
                    p-5
                    dark:border-ash/10
                    dark:bg-phthalo/45
                  "
                >
                  <div
                    className="
                      flex
                      flex-col
                      gap-4
                      sm:flex-row
                      sm:items-start
                      sm:justify-between
                    "
                  >
                    <div>
                      <p
                        className="
                          text-[10px]
                          font-bold
                          uppercase
                          tracking-[0.15em]
                          text-celestial
                          dark:text-ash
                        "
                      >
                        Supporting record
                      </p>

                      <h4
                        className="
                          mt-1
                          text-lg
                          font-semibold
                          text-deep-blue
                          dark:text-white
                        "
                      >
                        {selectedEvidence.category ??
                          (selectedEvidence.evidence_type === "MAINTENANCE"
                            ? "Maintenance"
                            : "Expense")}
                      </h4>

                      <p
                        className="
                          mt-1
                          text-xs
                          text-deep-blue/45
                          dark:text-white/40
                        "
                      >
                        {formatEvidenceDate(selectedEvidence.evidence_date)}
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() => setSelectedEvidence(null)}
                      className="
                        rounded-xl
                        bg-white
                        px-3
                        py-2
                        text-xs
                        font-semibold
                        text-deep-blue
                        shadow-sm
                        dark:bg-moss
                        dark:text-lime-soft
                      "
                    >
                      Close
                    </button>
                  </div>

                  <p
                    className="
                      mt-4
                      text-sm
                      leading-6
                      text-deep-blue/65
                      dark:text-white/60
                    "
                  >
                    {selectedEvidence.description ??
                      "No description available."}
                  </p>

                  <div
                    className="
                      mt-4
                      flex
                      flex-wrap
                      gap-2
                    "
                  >
                    {selectedEvidence.status && (
                      <span
                        className="
                          rounded-full
                          bg-celestial/10
                          px-3
                          py-1.5
                          text-[10px]
                          font-bold
                          uppercase
                          tracking-[0.12em]
                          text-celestial
                          dark:text-cyan
                        "
                      >
                        {selectedEvidence.status.replace("_", " ")}
                      </span>
                    )}

                    {selectedEvidence.amount && (
                      <span
                        className="
                          rounded-full
                          bg-moss/10
                          px-3
                          py-1.5
                          text-[10px]
                          font-bold
                          text-moss
                          dark:text-lime-soft
                        "
                      >
                        ${Number(selectedEvidence.amount).toFixed(2)}
                      </span>
                    )}

                    {selectedEvidence.unit_id && (
                      <span
                        className="
                          rounded-full
                          bg-ash/25
                          px-3
                          py-1.5
                          text-[10px]
                          font-bold
                          text-slate-green
                          dark:bg-white/10
                          dark:text-white/60
                        "
                      >
                        Unit record
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}