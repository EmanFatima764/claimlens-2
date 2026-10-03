import type { ReportData } from "@/types/report";
import { formatVerdictLabel } from "@/lib/report";

const LABEL_COLORS: Record<string, string> = {
  true: "#10b981",
  mostly_true: "#34d399",
  mixed: "#f59e0b",
  mostly_false: "#f97316",
  false: "#ef4444",
  unverified: "#64748b",
};

interface ReportSummaryProps {
  report: ReportData;
}

export default function ReportSummary({ report }: ReportSummaryProps) {
  const { verdict } = report;
  const tone = LABEL_COLORS[verdict.label] ?? "#64748b";
  return (
    <div style={{ display: "grid", gap: 16 }}>
      <h2 style={{ margin: 0, color: "#e2e8f0" }}>{report.title}</h2>

      <div style={{ background: "rgba(15,23,42,0.7)", border: `1px solid ${tone}66`, borderLeft: `4px solid ${tone}`, borderRadius: 12, padding: 18, display: "grid", gap: 10 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <span style={{ color: "#94a3b8", fontSize: 12, letterSpacing: 1, textTransform: "uppercase" }}>Most likely answer</span>
          <span style={{ background: tone, color: "white", borderRadius: 999, padding: "6px 12px", fontWeight: 700, textTransform: "uppercase" }}>
            {formatVerdictLabel(verdict.label)}
          </span>
        </div>
        <p style={{ color: "#e2e8f0", fontSize: 15, lineHeight: 1.7, margin: 0 }}>{report.summary}</p>
        {verdict.label !== "unverified" && (
          <div style={{ color: "#94a3b8", fontSize: 12 }}>
            Confidence: {(verdict.confidence * 100).toFixed(0)}% · Uncertainty: {(verdict.uncertainty * 100).toFixed(0)}%
          </div>
        )}
        {verdict.reviewRequired && (
          <div style={{ color: "#fbbf24", fontSize: 12, fontWeight: 600 }}>
            ⚠ Human review recommended — the evidence is thin, mixed, or in conflict.
          </div>
        )}
      </div>
    </div>
  );
}
