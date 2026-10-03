"use client";

import { useEffect, useRef, useState } from "react";
import { Investigation, StageGroup } from "@/types/investigation";
import { getInvestigationStatus } from "@/lib/investigations";

interface InvestigationStatusProps {
  investigationId: string;
  onCompleted?: (investigation: Investigation) => void;
}

const POLL_MS = 2000;
const MAX_CONSECUTIVE_ERRORS = 5;

const STAGES: Array<{ key: Exclude<StageGroup, "done">; title: string; hint: string }> = [
  { key: "claim", title: "Claim", hint: "Extract the claim" },
  { key: "research", title: "Research", hint: "Search the web" },
  { key: "sources", title: "Sources", hint: "Score credibility" },
  { key: "evidence", title: "Evidence", hint: "Read what sources say" },
];

const STATUS_COLORS: Record<Investigation["status"], string> = {
  draft: "#64748b",
  queued: "#64748b",
  running: "#f59e0b",
  completed: "#10b981",
  failed: "#ef4444",
};

function stageState(index: number, status: Investigation["status"], group?: StageGroup | null) {
  if (status === "completed" || group === "done") return "done";
  const active = STAGES.findIndex((s) => s.key === group);
  if (active === -1) return "pending";
  if (index < active) return "done";
  if (index === active) return status === "failed" ? "failed" : "active";
  return "pending";
}

export default function InvestigationStatus({ investigationId, onCompleted }: InvestigationStatusProps) {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Keep the latest callback in a ref so a new function identity never restarts polling.
  const onCompletedRef = useRef(onCompleted);
  useEffect(() => {
    onCompletedRef.current = onCompleted;
  });

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let errors = 0;

    async function poll() {
      try {
        const data = await getInvestigationStatus(investigationId);
        if (cancelled) return;
        errors = 0;
        setError(null);
        setInvestigation(data);
        if (data.status === "completed" || data.status === "failed") {
          onCompletedRef.current?.(data);
          return; // stop polling
        }
      } catch (err) {
        if (cancelled) return;
        errors += 1;
        setError(err instanceof Error ? err.message : "Failed to fetch status");
        if (errors >= MAX_CONSECUTIVE_ERRORS) return; // give up after repeated failures
      }
      timer = setTimeout(poll, POLL_MS);
    }

    setInvestigation(null);
    setError(null);
    poll();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [investigationId]);

  if (!investigation) {
    return error ? (
      <div style={{ color: "#fca5a5" }}>Error: {error}</div>
    ) : (
      <div style={{ color: "#cbd5e1" }}>Loading investigation status...</div>
    );
  }

  const color = STATUS_COLORS[investigation.status] ?? "#64748b";
  const verdict = investigation.final_verdict as { label?: string; confidence?: number } | null | undefined;
  const inProgress = investigation.status === "queued" || investigation.status === "running" || investigation.status === "draft";

  return (
    <div
      style={{
        background: "rgba(15,23,42,0.7)",
        border: "1px solid rgba(148,163,184,0.2)",
        borderLeft: `4px solid ${color}`,
        borderRadius: 12,
        padding: 16,
        display: "grid",
        gap: 14,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <strong style={{ color: "#e2e8f0" }}>{investigation.title}</strong>
        <span style={{ background: color, color: "white", borderRadius: 999, padding: "4px 10px", fontSize: 12, fontWeight: 700 }}>
          {investigation.status.toUpperCase()}
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: 8 }}>
        {STAGES.map((stage, i) => {
          const state = stageState(i, investigation.status, investigation.stage_group);
          const tone = state === "done" ? "#10b981" : state === "active" ? "#f59e0b" : state === "failed" ? "#ef4444" : "#475569";
          return (
            <div
              key={stage.key}
              style={{
                border: `1px solid ${tone}`,
                borderRadius: 10,
                padding: "8px 10px",
                opacity: state === "pending" ? 0.55 : 1,
              }}
            >
              <div style={{ color: tone, fontSize: 11, fontWeight: 700 }}>
                {state === "done" ? "✓" : `0${i + 1}`} {state === "active" ? "· working" : ""}
              </div>
              <div style={{ color: "#e2e8f0", fontWeight: 700 }}>{stage.title}</div>
              <div style={{ color: "#94a3b8", fontSize: 12 }}>{stage.hint}</div>
            </div>
          );
        })}
      </div>

      {inProgress && (
        <div style={{ color: "#cbd5e1", fontSize: 13 }}>
          {investigation.current_stage
            ? `Running: ${investigation.current_stage.replace(/_/g, " ")}…`
            : "Queued — starting shortly…"}
          {error && <span style={{ color: "#fca5a5" }}> (connection problem, retrying)</span>}
        </div>
      )}

      {investigation.status === "completed" && verdict?.label && (
        <div style={{ color: "#e2e8f0" }}>
          <strong>Most likely answer:</strong> {verdict.label.replace(/_/g, " ")}
          {typeof verdict.confidence === "number" && ` · ${Math.round(verdict.confidence * 100)}% confidence`}
        </div>
      )}

      {investigation.status === "failed" && (
        <div style={{ color: "#fca5a5" }}>{investigation.error || "The investigation failed."}</div>
      )}
    </div>
  );
}
