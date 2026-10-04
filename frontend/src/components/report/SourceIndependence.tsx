import type { IndependenceAnalysis, IndependenceLevel } from "@/types/report";

interface SourceIndependenceProps {
  analysis: IndependenceAnalysis | null;
}

const LEVEL_CONFIG: Record<IndependenceLevel, { label: string; color: string; bg: string }> = {
  high: { label: "High", color: "#10b981", bg: "rgba(16,185,129,0.12)" },
  medium: { label: "Medium", color: "#f59e0b", bg: "rgba(245,158,11,0.12)" },
  low: { label: "Low", color: "#ef4444", bg: "rgba(239,68,68,0.12)" },
  unknown: { label: "Unknown", color: "#64748b", bg: "rgba(100,116,139,0.12)" },
};

const RELATIONSHIP_COLORS: Record<string, string> = {
  independent: "#10b981",
  republished: "#ef4444",
  derived: "#f97316",
  same_publisher: "#f59e0b",
  unclear: "#64748b",
};

function IndependenceBadge({ level }: { level: IndependenceLevel }) {
  const cfg = LEVEL_CONFIG[level] ?? LEVEL_CONFIG.unknown;
  return (
    <span
      style={{
        background: cfg.bg,
        color: cfg.color,
        border: `1px solid ${cfg.color}44`,
        borderRadius: 999,
        padding: "4px 12px",
        fontSize: 12,
        fontWeight: 700,
        letterSpacing: 0.5,
        textTransform: "uppercase",
      }}
    >
      {cfg.label} Independence
    </span>
  );
}

function RatioBar({ ratio, color }: { ratio: number; color: string }) {
  const pct = Math.round(ratio * 100);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div
        style={{
          flex: 1,
          height: 6,
          borderRadius: 99,
          background: "rgba(148,163,184,0.2)",
          overflow: "hidden",
        }}
      >
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: 99 }} />
      </div>
      <span style={{ color: "#94a3b8", fontSize: 11, minWidth: 30 }}>{pct}%</span>
    </div>
  );
}

export default function SourceIndependence({ analysis }: SourceIndependenceProps) {
  if (!analysis) {
    return (
      <div style={{ color: "#94a3b8", fontSize: 13 }}>
        No source independence data available.
      </div>
    );
  }

  const cfg = LEVEL_CONFIG[analysis.overallIndependence] ?? LEVEL_CONFIG.unknown;

  return (
    <div style={{ display: "grid", gap: 14 }}>
      {/* Header card */}
      <div
        style={{
          background: "rgba(15,23,42,0.7)",
          border: `1px solid ${cfg.color}33`,
          borderLeft: `4px solid ${cfg.color}`,
          borderRadius: 10,
          padding: 14,
          display: "grid",
          gap: 10,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 10,
            flexWrap: "wrap",
          }}
        >
          <div>
            <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700, marginBottom: 2 }}>
              INDEPENDENT ORIGINS
            </div>
            <div style={{ color: "#e2e8f0", fontSize: 22, fontWeight: 700 }}>
              {analysis.independentSourceCount}
              <span style={{ color: "#64748b", fontSize: 14, fontWeight: 400 }}>
                {" "}/ {analysis.totalSourceCount} sources
              </span>
            </div>
          </div>
          <IndependenceBadge level={analysis.overallIndependence} />
        </div>

        <RatioBar ratio={analysis.independenceRatio} color={cfg.color} />

        {analysis.explanation && (
          <p style={{ color: "#cbd5e1", fontSize: 12, margin: 0, lineHeight: 1.6 }}>
            {analysis.explanation}
          </p>
        )}

        {analysis.llmFallback && (
          <div style={{ color: "#64748b", fontSize: 11 }}>
            ℹ Domain-heuristic fallback used (LLM unavailable)
          </div>
        )}
      </div>

      {/* Origin groups */}
      {analysis.sourceGroups.length > 0 && (
        <div>
          <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700, marginBottom: 8 }}>
            ORIGIN GROUPS
          </div>
          <div style={{ display: "grid", gap: 8 }}>
            {analysis.sourceGroups.map((group) => (
              <div
                key={group.groupId}
                style={{
                  background: "rgba(15,23,42,0.5)",
                  border: `1px solid ${group.isIndependentOrigin ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
                  borderRadius: 8,
                  padding: 10,
                  display: "grid",
                  gap: 6,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: 8,
                    flexWrap: "wrap",
                  }}
                >
                  <span style={{ color: "#e2e8f0", fontSize: 12, fontWeight: 600 }}>
                    {group.originDescription || `Group ${group.groupId + 1}`}
                  </span>
                  <span
                    style={{
                      color: group.isIndependentOrigin ? "#10b981" : "#ef4444",
                      fontSize: 11,
                      fontWeight: 700,
                    }}
                  >
                    {group.isIndependentOrigin ? "✓ Independent" : "✗ Not Independent"}
                  </span>
                </div>
                {group.sourceDomains.length > 0 && (
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {group.sourceDomains.filter(Boolean).map((domain, i) => (
                      <span
                        key={i}
                        style={{
                          background: "rgba(148,163,184,0.1)",
                          color: "#94a3b8",
                          border: "1px solid rgba(148,163,184,0.2)",
                          borderRadius: 4,
                          padding: "2px 7px",
                          fontSize: 11,
                        }}
                      >
                        {domain}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Relationships */}
      {analysis.relationships.length > 0 && (
        <div>
          <div style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700, marginBottom: 8 }}>
            SOURCE RELATIONSHIPS
          </div>
          <div style={{ display: "grid", gap: 6 }}>
            {analysis.relationships.map((rel, i) => {
              const relColor = RELATIONSHIP_COLORS[rel.relationship] ?? "#64748b";
              return (
                <div
                  key={i}
                  style={{
                    background: "rgba(15,23,42,0.5)",
                    border: "1px solid rgba(148,163,184,0.15)",
                    borderRadius: 8,
                    padding: "8px 12px",
                    display: "grid",
                    gap: 4,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                    <span style={{ color: "#94a3b8", fontSize: 12 }}>{rel.domainA || rel.sourceIdA}</span>
                    <span
                      style={{
                        color: relColor,
                        background: `${relColor}18`,
                        border: `1px solid ${relColor}44`,
                        borderRadius: 4,
                        padding: "1px 7px",
                        fontSize: 10,
                        fontWeight: 700,
                        textTransform: "uppercase",
                      }}
                    >
                      {rel.relationship}
                    </span>
                    <span style={{ color: "#94a3b8", fontSize: 12 }}>{rel.domainB || rel.sourceIdB}</span>
                  </div>
                  {rel.explanation && (
                    <p style={{ color: "#64748b", fontSize: 11, margin: 0, lineHeight: 1.5 }}>
                      {rel.explanation}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
