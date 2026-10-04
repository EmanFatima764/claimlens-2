export type InvestigationStatus = "draft" | "queued" | "running" | "completed" | "failed";

/** The agent stages shown in the progress tracker (one per agent). */
export type StageGroup = "claim" | "research" | "sources" | "evidence" | "conflicts" | "verdict" | "done";

export interface Investigation {
  id: string;
  title: string;
  description?: string;
  input_text?: string;
  source_type?: string;
  status: InvestigationStatus;
  workflow_status?: string;
  current_stage?: string | null;
  stage_group?: StageGroup | null;
  final_verdict?: Record<string, unknown> | null;
  error?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface CreateInvestigationPayload {
  title: string;
  /** The claim / text to fact-check. */
  input_text?: string;
  description?: string;
  source_type?: "text" | "url" | "pdf" | "audio";
  status?: string;
}
