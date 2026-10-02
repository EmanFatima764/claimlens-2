import type { ReportData } from "@/types/report";

interface ReportSummaryProps {
  report: ReportData;
}

export default function ReportSummary({ report }: ReportSummaryProps) {
  return (
    <div style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <h2 style={{ margin: 0, color: "#e2e8f0" }}>{report.title}</h2>
        <span
          style={{
            background: report.verdict.label === "true" ? "#10b981" : report.verdict.label === "false" ? "#ef4444" : report.verdict.label === "mixed" ? "#f59e0b" : "#64748b",
            color: "white",
            borderRadius: 999,
            padding: "6px 12px",
            fontWeight: 700,
            textTransform: "uppercase",
          }}
        >
          {report.verdict.label}
        </span>
      </div>

      <div style={{ background: "rgba(15,23,42,0.7)", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12, padding: 16 }}>
        <p style={{ color: "#e2e8f0", fontSize: 14, lineHeight: 1.8, margin: 0 }}>{report.summary}</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
        <div style={{ background: "rgba(15,23,42,0.7)", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12, padding: 16 }}>
          <div style={{ color: "#94a3b8", fontSize: 12, marginBottom: 8 }}>Confidence</div>
          <div style={{ color: "#e2e8f0", fontWeight: 700, fontSize: 24 }}>{(report.verdict.confidence * 100).toFixed(0)}%</div>
        </div>
        <div style={{ background: "rgba(15,23,42,0.7)", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12, padding: 16 }}>
          <div style={{ color: "#94a3b8", fontSize: 12, marginBottom: 8 }}>Uncertainty</div>
          <div style={{ color: "#e2e8f0", fontWeight: 700, fontSize: 24 }}>{(report.verdict.uncertainty * 100).toFixed(0)}%</div>
        </div>
        <div style={{ background: "rgba(15,23,42,0.7)", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12, padding: 16 }}>
          <div style={{ color: "#94a3b8", fontSize: 12, marginBottom: 8 }}>Review</div>
          <div style={{ color: "#e2e8f0", fontWeight: 700, fontSize: 24 }}>{report.verdict.reviewRequired ? "Required" : "Not required"}</div>
        </div>
      </div>
    </div>
  );
}
