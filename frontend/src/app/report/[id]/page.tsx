import type { ReportData } from "@/types/report";
import { getMockReport } from "@/lib/report";
import ReportSummary from "@/components/report/ReportSummary";
import EvidenceCard from "@/components/report/EvidenceCard";
import SourceList from "@/components/report/SourceList";
import ConflictList from "@/components/report/ConflictList";

export default function ReportPage({ params }: { params: { id: string } }) {
  const report: ReportData = getMockReport(params.id);

  return (
    <main style={{ maxWidth: 1280, margin: "0 auto", padding: "2rem 1.5rem", color: "#e2e8f0" }}>
      <div style={{ marginBottom: 24 }}>
        <a href="/investigate" style={{ color: "#7dd3fc", textDecoration: "none" }}>← Back to investigation</a>
      </div>

      <ReportSummary report={report} />

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 24, marginTop: 24 }}>
        <section>
          <h3 style={{ margin: "0 0 12px", color: "#e2e8f0" }}>Claim</h3>
          <div style={{ background: "rgba(15,23,42,0.7)", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12, padding: 16 }}>
            <p style={{ margin: 0, lineHeight: 1.8, color: "#e2e8f0" }}>{report.claimText}</p>
          </div>

          <h3 style={{ margin: "24px 0 12px", color: "#e2e8f0" }}>Evidence</h3>
          <div style={{ display: "grid", gap: 16 }}>
            {report.evidence.map((item) => (
              <EvidenceCard
                key={item.id}
                evidence={item}
                source={report.sources.find((source) => source.id === item.sourceId)}
              />
            ))}
          </div>
        </section>

        <aside style={{ display: "grid", gap: 24 }}>
          <div>
            <h3 style={{ margin: "0 0 12px", color: "#e2e8f0" }}>Sources</h3>
            <SourceList sources={report.sources} />
          </div>

          <div>
            <h3 style={{ margin: "0 0 12px", color: "#e2e8f0" }}>Conflicts</h3>
            <ConflictList conflicts={report.conflicts} />
          </div>
        </aside>
      </div>

      <section style={{ marginTop: 32 }}>
        <h3 style={{ margin: "0 0 12px", color: "#e2e8f0" }}>Evidence Graph</h3>
        <div style={{ position: "relative", height: 360, background: "rgba(15,23,42,0.7)", borderRadius: 16, border: "1px solid rgba(148,163,184,0.2)", overflow: "hidden" }}>
          {report.graph.nodes.map((node) => (
            <div
              key={node.id}
              style={{
                position: "absolute",
                left: node.x,
                top: node.y,
                transform: "translate(-50%, -50%)",
                minWidth: 110,
                background: node.type === "claim" ? "#3b82f6" : node.type === "source" ? "#10b981" : "#f59e0b",
                color: "white",
                borderRadius: 999,
                padding: "8px 12px",
                fontSize: 12,
                fontWeight: 700,
                boxShadow: "0 4px 12px rgba(15,23,42,0.25)",
              }}
            >
              {node.label}
            </div>
          ))}
          {report.graph.edges.map((edge, idx) => {
            const sourceNode = report.graph.nodes.find((n) => n.id === edge.source);
            const targetNode = report.graph.nodes.find((n) => n.id === edge.target);
            if (!sourceNode || !targetNode) return null;

            const x1 = sourceNode.x;
            const y1 = sourceNode.y;
            const x2 = targetNode.x;
            const y2 = targetNode.y;

            return (
              <div
                key={`${edge.source}-${edge.target}-${idx}`}
                style={{
                  position: "absolute",
                  left: Math.min(x1, x2),
                  top: Math.min(y1, y2),
                  width: Math.abs(x2 - x1),
                  height: Math.abs(y2 - y1),
                  borderTop: "2px dashed rgba(125, 211, 252, 0.7)",
                  transform: x2 < x1 ? "skewY(0deg)" : "none",
                }}
              >
                <span style={{ position: "absolute", left: 8, top: -18, color: "#7dd3fc", fontSize: 11 }}>{edge.label}</span>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
