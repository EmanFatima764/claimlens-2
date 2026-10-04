import type { EvidenceRecord, SourceRecord } from "@/types/report";

interface EvidenceCardProps {
  evidence: EvidenceRecord;
  source: SourceRecord | undefined;
}

export default function EvidenceCard({ evidence, source }: EvidenceCardProps) {
  const tone = evidence.type === "supporting" ? "#10b981" : evidence.type === "contradicting" ? "#ef4444" : "#94a3b8";

  return (
    <div style={{ border: `1px solid ${tone}33`, background: "rgba(15,23,42,0.7)", borderRadius: 12, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <span style={{ background: tone, color: "white", padding: "4px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700, textTransform: "uppercase" }}>
          {evidence.type}
        </span>
        <span style={{ color: "#cbd5e1", fontSize: 12 }}>Relevance: {(evidence.relevanceScore * 100).toFixed(0)}%</span>
      </div>
      <p style={{ color: "#e2e8f0", lineHeight: 1.7, margin: 0 }}>{evidence.text}</p>
      {source && (
        <div style={{ marginTop: 12, color: "#cbd5e1", fontSize: 12 }}>
          <strong>Source:</strong>{" "}
          {source.url ? <a href={source.url} target="_blank" rel="noreferrer" style={{ color: "#7dd3fc" }}>{source.title}</a> : source.title} · {source.publisher}
        </div>
      )}
    </div>
  );
}
