import type { ConflictRecord } from "@/types/report";

interface ConflictListProps {
  conflicts: ConflictRecord[];
}

export default function ConflictList({ conflicts }: ConflictListProps) {
  if (!conflicts.length) {
    return <div style={{ color: "#cbd5e1" }}>No material conflicts detected.</div>;
  }

  return (
    <div style={{ display: "grid", gap: 12 }}>
      {conflicts.map((conflict) => (
        <div key={conflict.id} style={{ background: "rgba(15,23,42,0.7)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 12, padding: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <strong style={{ color: "#fca5a5" }}>{conflict.type}</strong>
            <span style={{ color: "#fca5a5" }}>Severity: {(conflict.severity * 100).toFixed(0)}%</span>
          </div>
          <p style={{ color: "#e2e8f0", margin: 0, lineHeight: 1.7 }}>{conflict.explanation}</p>
        </div>
      ))}
    </div>
  );
}
