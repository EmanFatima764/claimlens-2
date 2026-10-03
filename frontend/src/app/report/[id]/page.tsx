import type { ReportData } from "@/types/report";
import { getMockReport } from "@/lib/report";
import ReportSummary from "@/components/report/ReportSummary";
import EvidenceCard from "@/components/report/EvidenceCard";
import SourceList from "@/components/report/SourceList";
import ConflictList from "@/components/report/ConflictList";
import ReportChat from "@/components/report/ReportChat";

export default function ReportPage({ params }: { params: { id: string } }) {
  const report: ReportData = getMockReport(params.id);

  return (
    <main className="report-shell">
      <div className="report-topbar">
        <a href="/investigate" className="secondary-button" style={{ width: "fit-content" }}>← Back to investigation</a>
        <span className="report-badge">Case #{report.id}</span>
      </div>

      <ReportSummary report={report} />

      <div className="report-layout" style={{ marginTop: "1.4rem" }}>
        <section>
          <h3 style={{ margin: "0 0 12px" }}>Claim</h3>
          <div className="glass-section claim-panel">
            <p style={{ margin: 0 }}>{report.claimText}</p>
          </div>

          <h3 style={{ margin: "1.5rem 0 12px" }}>Evidence</h3>
          <div className="evidence-stack">
            {report.evidence.map((item) => (
              <EvidenceCard
                key={item.id}
                evidence={item}
                source={report.sources.find((source) => source.id === item.sourceId)}
              />
            ))}
          </div>
        </section>

        <aside className="evidence-stack" style={{ gap: "1.5rem" }}>
          <div>
            <h3 style={{ margin: "0 0 12px" }}>Sources</h3>
            <SourceList sources={report.sources} />
          </div>

          <div>
            <h3 style={{ margin: "0 0 12px" }}>Conflicts</h3>
            <ConflictList conflicts={report.conflicts} />
          </div>
        </aside>
      </div>

      <section style={{ marginTop: "2rem" }}>
        <h3 style={{ margin: "0 0 12px" }}>Evidence graph</h3>
        <div className="graph-panel">
          {report.graph.nodes.map((node) => (
            <div
              key={node.id}
              className="graph-node"
              style={{
                left: node.x,
                top: node.y,
                background:
                  node.type === "claim" ? "linear-gradient(135deg,#4f7cff,#62d7ff)" :
                  node.type === "source" ? "linear-gradient(135deg,#1ec58b,#73f0c1)" :
                  "linear-gradient(135deg,#ffb454,#ffc777)",
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
                  borderTop: "2px dashed rgba(98, 215, 255, 0.8)",
                }}
              >
                <span style={{ position: "absolute", left: 8, top: -18, color: "#bfeaff", fontSize: 11 }}>{edge.label}</span>
              </div>
            );
          })}
        </div>
      </section>

      <ReportChat report={report} />
    </main>
  );
}
