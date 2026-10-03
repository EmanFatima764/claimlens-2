export type EvidenceType = "supporting" | "contradicting" | "neutral";
export type VerdictLabel = "true" | "mostly_true" | "mixed" | "mostly_false" | "false" | "unverified";

export interface SourceRecord {
  id: string;
  title: string;
  url: string;
  publisher: string;
  sourceType: string;
  qualityScore: number;
  relevanceScore: number;
}

export interface EvidenceRecord {
  id: string;
  claimId: string;
  sourceId: string;
  text: string;
  type: EvidenceType;
  relevanceScore: number;
  confidence: number;
}

export interface ConflictRecord {
  id: string;
  evidenceAId: string;
  evidenceBId: string;
  type: string;
  severity: number;
  explanation: string;
}

export interface VerdictSummary {
  label: VerdictLabel;
  confidence: number;
  uncertainty: number;
  explanation: string;
  reviewRequired: boolean;
}

export interface ReportData {
  id: string;
  title: string;
  status: "draft" | "running" | "completed" | "failed";
  claimText: string;
  summary: string;
  verdict: VerdictSummary;
  sources: SourceRecord[];
  evidence: EvidenceRecord[];
  conflicts: ConflictRecord[];
  graph: {
    nodes: Array<{ id: string; label: string; type: string; x: number; y: number }>;
    edges: Array<{ source: string; target: string; label: string }>;
  };
}
