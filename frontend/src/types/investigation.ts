export type InvestigationStatus = "draft" | "running" | "completed" | "failed";

export interface Investigation {
  id: string;
  title: string;
  description?: string;
  input_text?: string;
  source_type?: string;
  status: InvestigationStatus;
  workflow_status?: string;
  final_verdict?: Record<string, unknown>;
  error?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateInvestigationPayload {
  title: string;
  description?: string;
  source_type?: "text" | "url" | "pdf" | "audio";
  status?: string;
}
