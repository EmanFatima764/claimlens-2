import type { SourceRecord } from "@/types/report";

interface SourceListProps {
  sources: SourceRecord[];
}

export default function SourceList({ sources }: SourceListProps) {
  return (
    <div style={{ display: "grid", gap: 12 }}>
      {sources.map((source) => (
        <div key={source.id} style={{ background: "rgba(15,23,42,0.7)", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12, padding: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <strong style={{ color: "#e2e8f0" }}>{source.title}</strong>
            <span
              style={{
                background: source.qualityScore >= 0.8 ? "#10b981" : source.qualityScore >= 0.55 ? "#f59e0b" : "#ef4444",
                color: "white",
                borderRadius: 999,
                padding: "4px 8px",
                fontSize: 11,
                fontWeight: 700,
              }}
            >
              {source.sourceType}
            </span>
          </div>
          <p style={{ color: "#cbd5e1", margin: "8px 0 0" }}>{source.publisher}</p>
          <a href={source.url} target="_blank" rel="noreferrer" style={{ color: "#7dd3fc", wordBreak: "break-all" }}>
            {source.url}
          </a>
          <div style={{ marginTop: 8, color: "#cbd5e1", fontSize: 12 }}>
            Quality score: {(source.qualityScore * 100).toFixed(0)}% · Relevance: {(source.relevanceScore * 100).toFixed(0)}%
          </div>
        </div>
      ))}
    </div>
  );
}
