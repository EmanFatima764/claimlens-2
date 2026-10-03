import type {
  ConflictRecord,
  EvidenceRecord,
  EvidenceType,
  ReportData,
  SourceRecord,
  VerdictLabel,
} from "@/types/report";
import { API_BASE_URL } from "@/lib/api";

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

/* ------------------------------------------------------------------ */
/*  Real report: GET /api/v1/reports/{id}  ->  ReportData             */
/* ------------------------------------------------------------------ */

interface ApiReport {
  investigation: { id: string; title?: string; status?: string; input_text?: string };
  claims: Array<{ id: string; text: string }>;
  sources: Array<{
    id: string;
    title?: string;
    url?: string;
    publisher?: string;
    domain?: string;
    source_type?: string;
    quality_score?: number;
    relevance_score?: number;
  }>;
  evidence: Array<{
    id: string;
    claim_id?: string;
    source_id?: string;
    evidence_text: string;
    stance?: string;
    relevance_score?: number;
    confidence?: number;
  }>;
  conflicts: Array<{
    id: string;
    evidence_a_id?: string;
    evidence_b_id?: string;
    conflict_type?: string;
    severity?: number;
    explanation?: string;
  }>;
  verdict: {
    label?: string;
    explanation?: string;
    confidence?: number;
    uncertainty?: number;
    review_required?: boolean;
  } | null;
}

const num = (v: unknown, fallback = 0) => (typeof v === "number" && Number.isFinite(v) ? v : fallback);
const VERDICT_LABELS: VerdictLabel[] = ["true", "mostly_true", "mixed", "mostly_false", "false", "unverified"];

export function formatVerdictLabel(label: string): string {
  return label.replace(/_/g, " ");
}

/** Fetch a finished (or in-progress) report from the backend. Returns null if it does not exist. */
export async function getReport(id: string): Promise<ReportData | null> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${encodeURIComponent(id)}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Report request failed (${res.status})`);
  return adaptReport((await res.json()) as ApiReport);
}

/**
 * Maps the backend payload to the shape the report components use.
 * Database uuids are replaced with short display ids (src-1, ev-1, conf-1, claim-1) because the
 * chat assistant cites items by those ids and ReportChat highlights them.
 */
export function adaptReport(api: ApiReport): ReportData {
  const claimIds = new Map(api.claims.map((c, i) => [c.id, `claim-${i + 1}`]));
  const srcIds = new Map(api.sources.map((s, i) => [s.id, `src-${i + 1}`]));
  const evIds = new Map(api.evidence.map((e, i) => [e.id, `ev-${i + 1}`]));

  const sources: SourceRecord[] = api.sources.map((s) => ({
    id: srcIds.get(s.id)!,
    title: s.title || s.domain || s.url || "Untitled source",
    url: s.url ?? "",
    publisher: s.publisher || s.domain || "Unknown",
    sourceType: s.source_type || "other",
    qualityScore: num(s.quality_score, 0.5),
    relevanceScore: num(s.relevance_score, 0.5),
  }));

  const evidence: EvidenceRecord[] = api.evidence.map((e) => ({
    id: evIds.get(e.id)!,
    claimId: claimIds.get(e.claim_id ?? "") ?? "",
    sourceId: srcIds.get(e.source_id ?? "") ?? "",
    text: e.evidence_text,
    type: (["supporting", "contradicting", "neutral"].includes(e.stance ?? "") ? e.stance : "neutral") as EvidenceType,
    relevanceScore: num(e.relevance_score, 0.5),
    confidence: num(e.confidence, 0.5),
  }));

  const conflicts: ConflictRecord[] = api.conflicts.map((c, i) => ({
    id: `conf-${i + 1}`,
    evidenceAId: evIds.get(c.evidence_a_id ?? "") ?? "",
    evidenceBId: evIds.get(c.evidence_b_id ?? "") ?? "",
    type: c.conflict_type || "conflict",
    severity: num(c.severity, 0.5),
    explanation: c.explanation || "",
  }));

  const v = api.verdict;
  const label = (VERDICT_LABELS.includes(v?.label as VerdictLabel) ? v?.label : "unverified") as VerdictLabel;
  const status = api.investigation.status;

  return {
    id: api.investigation.id,
    title: api.investigation.title || "Investigation",
    status: status === "completed" || status === "failed" ? status : "running",
    claimText: api.claims.length
      ? api.claims.map((c) => c.text).join(" • ")
      : api.investigation.input_text || "",
    summary: v?.explanation || (v ? "" : "This investigation is still running. Refresh in a moment."),
    verdict: {
      label,
      confidence: num(v?.confidence),
      uncertainty: num(v?.uncertainty, 1),
      explanation: v?.explanation || "",
      reviewRequired: v?.review_required ?? true,
    },
    sources,
    evidence,
    conflicts,
    graph: buildGraph(api, claimIds, srcIds, evIds),
  };
}

function buildGraph(
  api: ApiReport,
  claimIds: Map<string, string>,
  srcIds: Map<string, string>,
  evIds: Map<string, string>
): ReportData["graph"] {
  const ROW = 62;
  const claims = api.claims.slice(0, 3);
  const sources = api.sources.slice(0, 5);
  const shownSrc = new Set(sources.map((s) => s.id));
  const evidence = api.evidence.filter((e) => e.source_id && shownSrc.has(e.source_id)).slice(0, 5);

  const nodes: ReportData["graph"]["nodes"] = [
    ...claims.map((c, i) => ({ id: claimIds.get(c.id)!, label: `Claim ${i + 1}`, type: "claim", x: 90, y: 40 + i * 95 })),
    ...sources.map((s, i) => ({
      id: srcIds.get(s.id)!,
      label: (s.publisher || s.domain || "Source").slice(0, 18),
      type: "source",
      x: 320,
      y: 30 + i * ROW,
    })),
    ...evidence.map((e, i) => ({
      id: evIds.get(e.id)!,
      label: e.stance === "supporting" ? "Support" : e.stance === "contradicting" ? "Conflict" : "Context",
      type: "evidence",
      x: 540,
      y: 30 + i * ROW,
    })),
  ];

  const edges: ReportData["graph"]["edges"] = [];
  const seen = new Set<string>();
  for (const e of evidence) {
    const claimNode = claimIds.get(e.claim_id ?? "");
    const srcNode = srcIds.get(e.source_id ?? "");
    const evNode = evIds.get(e.id);
    if (!srcNode || !evNode) continue;
    const key = `${claimNode}>${srcNode}`;
    if (claimNode && nodes.some((n) => n.id === claimNode) && !seen.has(key)) {
      seen.add(key);
      edges.push({
        source: claimNode,
        target: srcNode,
        label: e.stance === "supporting" ? "supports" : e.stance === "contradicting" ? "contradicts" : "mentions",
      });
    }
    edges.push({ source: srcNode, target: evNode, label: "evidence" });
  }
  return { nodes, edges };
}
