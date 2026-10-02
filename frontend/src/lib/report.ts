import type { EvidenceRecord, SourceRecord } from "@/types/report";

export function formatScore(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

export function getEvidenceTone(type: EvidenceRecord["type"]): string {
  switch (type) {
    case "supporting":
      return "#10b981";
    case "contradicting":
      return "#ef4444";
    default:
      return "#94a3b8";
  }
}

export function getSourceBadgeTone(score: number): string {
  if (score >= 0.8) return "#10b981";
  if (score >= 0.55) return "#f59e0b";
  return "#ef4444";
}

export function getMockReport(reportId: string): {
  id: string;
  title: string;
  status: "completed";
  claimText: string;
  summary: string;
  verdict: {
    label: "mixed";
    confidence: number;
    uncertainty: number;
    explanation: string;
    reviewRequired: boolean;
  };
  sources: SourceRecord[];
  evidence: EvidenceRecord[];
  conflicts: Array<{ id: string; evidenceAId: string; evidenceBId: string; type: string; severity: number; explanation: string }>;
  graph: {
    nodes: Array<{ id: string; label: string; type: string; x: number; y: number }>;
    edges: Array<{ source: string; target: string; label: string }>;
  };
} {
  return {
    id: reportId,
    title: "Startup traction claim verification",
    status: "completed",
    claimText:
      "The company has 50,000 active users and grew revenue by 180% in the last 12 months.",
    summary:
      "This claim is partially supported by independent evidence. User volume is consistent with published reporting, but some revenue growth figures remain under-audited and may require follow-up verification.",
    verdict: {
      label: "mixed",
      confidence: 0.68,
      uncertainty: 0.42,
      explanation:
        "Independent source overlap supports the user count, while the revenue growth figure is less strongly corroborated and may rely on a single source chain.",
      reviewRequired: true,
    },
    sources: [
      {
        id: "src-1",
        title: "Company annual report",
        url: "https://example.com/company-annual-report",
        publisher: "Company",
        sourceType: "primary",
        qualityScore: 0.78,
        relevanceScore: 0.9,
      },
      {
        id: "src-2",
        title: "Industry growth report",
        url: "https://example.com/industry-report",
        publisher: "Industry Research Group",
        sourceType: "secondary",
        qualityScore: 0.82,
        relevanceScore: 0.86,
      },
      {
        id: "src-3",
        title: "Trade publication coverage",
        url: "https://example.com/trade-publication",
        publisher: "Trade Journal",
        sourceType: "news",
        qualityScore: 0.6,
        relevanceScore: 0.7,
      },
    ],
    evidence: [
      {
        id: "ev-1",
        claimId: "claim-1",
        sourceId: "src-1",
        text: "The company reported 50,000 active users in the latest annual report and investor update.",
        type: "supporting",
        relevanceScore: 0.94,
        confidence: 0.8,
      },
      {
        id: "ev-2",
        claimId: "claim-1",
        sourceId: "src-2",
        text: "Industry benchmark data mirrors the user base scale and indicates strong adoption trends in this market segment.",
        type: "supporting",
        relevanceScore: 0.82,
        confidence: 0.74,
      },
      {
        id: "ev-3",
        claimId: "claim-2",
        sourceId: "src-3",
        text: "One trade article reports the revenue increase at 180%, but the exact mix of revenue stream definitions remains unclear.",
        type: "contradicting",
        relevanceScore: 0.76,
        confidence: 0.62,
      },
    ],
    conflicts: [
      {
        id: "conf-1",
        evidenceAId: "ev-1",
        evidenceBId: "ev-3",
        type: "measurement_definition",
        severity: 0.56,
        explanation: "The reported revenue growth is not fully aligned on the definition of revenue base used across sources.",
      },
    ],
    graph: {
      nodes: [
        { id: "claim-1", label: "Claim", type: "claim", x: 120, y: 120 },
        { id: "src-1", label: "Company report", type: "source", x: 320, y: 60 },
        { id: "src-2", label: "Industry report", type: "source", x: 320, y: 160 },
        { id: "src-3", label: "Trade article", type: "source", x: 320, y: 260 },
        { id: "ev-1", label: "Support", type: "evidence", x: 520, y: 70 },
        { id: "ev-3", label: "Conflict", type: "evidence", x: 520, y: 220 },
      ],
      edges: [
        { source: "claim-1", target: "src-1", label: "supports" },
        { source: "claim-1", target: "src-2", label: "supports" },
        { source: "claim-1", target: "src-3", label: "contradicts" },
        { source: "src-1", target: "ev-1", label: "evidence" },
        { source: "src-3", target: "ev-3", label: "evidence" },
      ],
    },
  };
}
