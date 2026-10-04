export type EvidenceType = "supporting" | "contradicting" | "neutral";
export type VerdictLabel = "true" | "mostly_true" | "mixed" | "mostly_false" | "false" | "unverified";
export type VerificationStatus = "supported" | "partially_supported" | "refuted" | "insufficient_evidence";
export type IndependenceLevel = "high" | "medium" | "low" | "unknown";

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

/** Per-claim result from VerificationAgent */
export interface VerifiedClaim {
  id?: string;
  claimId: string;
  claimText?: string;         // enriched on the frontend by matching against claims list
  verificationStatus: VerificationStatus;
  confidence: number;
  supportingEvidence: string[];
  contradictingEvidence: string[];
  reasoning: string;
  unresolvedIssues: string[];
  llmFallback: boolean;
}

/** One origin group from IndependenceAgent */
export interface SourceGroup {
  groupId: number;
  sourceIds: string[];
  sourceDomains: string[];
  originDescription: string;
  isIndependentOrigin: boolean;
}

/** Pairwise relationship between two sources */
export interface SourceRelationship {
  sourceIdA: string;
  sourceIdB: string;
  domainA: string;
  domainB: string;
  relationship: string;
  explanation: string;
}

/** Full independence analysis from IndependenceAgent */
export interface IndependenceAnalysis {
  independentSourceCount: number;
  totalSourceCount: number;
  independenceRatio: number;
  sourceGroups: SourceGroup[];
  relationships: SourceRelationship[];
  overallIndependence: IndependenceLevel;
  explanation: string;
  llmFallback: boolean;
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
  verifiedClaims: VerifiedClaim[];
  independenceAnalysis: IndependenceAnalysis | null;
  graph: {
    nodes: Array<{ id: string; label: string; type: string; x: number; y: number }>;
    edges: Array<{ source: string; target: string; label: string }>;
  };
}
