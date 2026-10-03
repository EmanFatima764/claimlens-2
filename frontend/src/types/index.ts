export type InvestigationStatus = "draft" | "queued" | "running" | "completed" | "failed";

export interface InvestigationSummary {
  id: string;
  title: string;
  description?: string;
  status: InvestigationStatus;
}

export interface VerdictSummary {
  label: string;
  confidence: number;
  uncertainty: number;
}
