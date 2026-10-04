import type { ReportData } from "@/types/report";
import { getMockReport, getReport } from "@/lib/report";
import ReportSummary from "@/components/report/ReportSummary";
import EvidenceCard from "@/components/report/EvidenceCard";
import SourceList from "@/components/report/SourceList";
import ConflictList from "@/components/report/ConflictList";
import ReportChat from "@/components/report/ReportChat";

// Always render with fresh data from the backend.
export const dynamic = "force-dynamic";

type Params = { id: string };

function Notice({ title, message }: { title: string; message: string }) {
  return (
    <main className="report-shell">
      <div className="report-topbar">
        <a href="/investigate" className="secondary-button" style={{ width: "fit-content" }}>← Back to investigation</a>
      </div>
      <div className="glass-section" style={{ marginTop: "1.4rem" }}>
        <h2 style={{ marginTop: 0 }}>{title}</h2>
        <p style={{ marginBottom: 0 }}>{message}</p>
      </div>
    </main>
  );
}

export default async function ReportPage({ params }: { params: Params | Promise<Params> }) {
  const { id } = await Promise.resolve(params);

  let report: ReportData | null;
  if (id === "sample") {
    report = getMockReport(id);
  } else {
    try {
      report = await getReport(id);
    } catch {
      return <Notice title="Could not load the report" message="The backend is unreachable. Check that it is running and that NEXT_PUBLIC_API_URL is correct, then refresh." />;
    }
  }

  if (!report) {
    return <Notice title="Report not found" message="No investigation exists with this id." />;
  }

  const inProgress = report.status === "running" || report.status === "draft";
  const failed = report.status === "failed";

  return (
    <main className="report-shell">
      <div className="report-topbar">
        <a href="/investigate" className="secondary-button" style={{ width: "fit-content" }}>← Back to investigation</a>
        <span className="report-badge">Case #{id === "sample" ? report.id : report.id.slice(0, 8)}</span>
      </div>

      {inProgress && (
        <div className="glass-section" style={{ margin: "1rem 0" }}>
          This investigation is still running. <a href={`/report/${id}`} style={{ color: "#7dd3fc" }}>Refresh</a> to see the latest results.
        </div>
      )}
      {failed && (
        <div className="glass-section" style={{ margin: "1rem 0", borderColor: "rgba(239,68,68,0.4)" }}>
          This check failed before the evidence could be collected. Start a new one to try again.
        </div>
      )}

      <ReportSummary report={report} />

      <div className="report-layout" style={{ marginTop: "1.4rem" }}>
        <section>
          <h3 style={{ margin: "0 0 12px" }}>Claim</h3>
          <div className="glass-section claim-panel">
            <p style={{ margin: 0 }}>{report.claimText}</p>
          </div>

          <h3 style={{ margin: "1.5rem 0 12px" }}>Evidence</h3>
          <div className="evidence-stack">
            {report.evidence.length === 0 && <div style={{ color: "#cbd5e1" }}>No relevant evidence was found for this claim.</div>}
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
            <h3 style={{ margin: "0 0 12px" }}>Conflicts</h3>
            <ConflictList conflicts={report.conflicts} />
          </div>
          <div>
            <h3 style={{ margin: "0 0 12px" }}>Sources</h3>
            <SourceList sources={report.sources} />
          </div>
        </aside>
      </div>

      <ReportChat report={report} />
    </main>
  );
}
