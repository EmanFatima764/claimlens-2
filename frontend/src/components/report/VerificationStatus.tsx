import type { VerifiedClaim, VerificationStatus } from "@/types/report";

interface VerificationStatusProps {
  verifiedClaims: VerifiedClaim[];
}

const STATUS_CONFIG: Record<
  VerificationStatus,
  { label: string; color: string; bg: string; icon: string }
> = {
  supported: {
    label: "Supported",
    color: "#10b981",
    bg: "rgba(16,185,129,0.12)",
    icon: "✓",
  },
  partially_supported: {
    label: "Partially Supported",
    color: "#f59e0b",
    bg: "rgba(245,158,11,0.12)",
    icon: "◑",
  },
  refuted: {
    label: "Refuted",
    color: "#ef4444",
    bg: "rgba(239,68,68,0.12)",
    icon: "✗",
  },
  insufficient_evidence: {
    label: "Insufficient Evidence",
    color: "#64748b",
    bg: "rgba(100,116,139,0.12)",
    icon: "?",
  },
};

function StatusBadge({ status }: { status: VerificationStatus }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.insufficient_evidence;
  return (
    <span
      style={{
        background: cfg.bg,
        color: cfg.color,
        border: `1px solid ${cfg.color}44`,
        borderRadius: 999,
        padding: "3px 10px",
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: 0.5,
        textTransform: "uppercase",
        whiteSpace: "nowrap",
      }}
    >
      {cfg.icon} {cfg.label}
    </span>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = value >= 0.7 ? "#10b981" : value >= 0.4 ? "#f59e0b" : "#ef4444";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div
        style={{
          flex: 1,
          height: 5,
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

export default function VerificationStatus({ verifiedClaims }: VerificationStatusProps) {
  if (!verifiedClaims || verifiedClaims.length === 0) {
    return (
      <div style={{ color: "#94a3b8", fontSize: 13 }}>
        No claim verification data available.
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: 12 }}>
      {verifiedClaims.map((vc, idx) => {
        const cfg = STATUS_CONFIG[vc.verificationStatus] ?? STATUS_CONFIG.insufficient_evidence;
        return (
          <div
            key={vc.claimId || idx}
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
            {/* Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: 10,
                flexWrap: "wrap",
              }}
            >
              <span style={{ color: "#94a3b8", fontSize: 11, fontWeight: 700 }}>
                CLAIM {idx + 1}
              </span>
              <StatusBadge status={vc.verificationStatus} />
            </div>

            {/* Claim text */}
            {vc.claimText && (
              <p style={{ color: "#e2e8f0", fontSize: 13, margin: 0, lineHeight: 1.6 }}>
                {vc.claimText}
              </p>
            )}

            {/* Confidence */}
            <div>
              <div style={{ color: "#94a3b8", fontSize: 11, marginBottom: 4 }}>
                Confidence
              </div>
              <ConfidenceBar value={vc.confidence} />
            </div>

            {/* Reasoning */}
            {vc.reasoning && (
              <p style={{ color: "#cbd5e1", fontSize: 12, margin: 0, lineHeight: 1.6 }}>
                {vc.reasoning}
              </p>
            )}

            {/* Supporting evidence */}
            {vc.supportingEvidence.length > 0 && (
              <div>
                <div
                  style={{ color: "#10b981", fontSize: 11, fontWeight: 700, marginBottom: 4 }}
                >
                  ✓ Supporting
                </div>
                <ul style={{ margin: 0, paddingLeft: 16, display: "grid", gap: 4 }}>
                  {vc.supportingEvidence.map((e, i) => (
                    <li key={i} style={{ color: "#a7f3d0", fontSize: 12, lineHeight: 1.5 }}>
                      {e}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Contradicting evidence */}
            {vc.contradictingEvidence.length > 0 && (
              <div>
                <div
                  style={{ color: "#ef4444", fontSize: 11, fontWeight: 700, marginBottom: 4 }}
                >
                  ✗ Contradicting
                </div>
                <ul style={{ margin: 0, paddingLeft: 16, display: "grid", gap: 4 }}>
                  {vc.contradictingEvidence.map((e, i) => (
                    <li key={i} style={{ color: "#fca5a5", fontSize: 12, lineHeight: 1.5 }}>
                      {e}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Unresolved issues */}
            {vc.unresolvedIssues.length > 0 && (
              <div>
                <div
                  style={{ color: "#f59e0b", fontSize: 11, fontWeight: 700, marginBottom: 4 }}
                >
                  ⚠ Unresolved
                </div>
                <ul style={{ margin: 0, paddingLeft: 16, display: "grid", gap: 4 }}>
                  {vc.unresolvedIssues.map((issue, i) => (
                    <li key={i} style={{ color: "#fde68a", fontSize: 12, lineHeight: 1.5 }}>
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {vc.llmFallback && (
              <div style={{ color: "#64748b", fontSize: 11 }}>
                ℹ Stance-count fallback used (LLM unavailable)
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
