import { Investigation, CreateInvestigationPayload } from "@/types/investigation";
import { apiRequest } from "@/lib/api";

export async function createInvestigation(
  payload: CreateInvestigationPayload
): Promise<Investigation> {
  return apiRequest<Investigation>("/api/v1/investigations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getInvestigation(id: string): Promise<Investigation> {
  return apiRequest<Investigation>(`/api/v1/investigations/${id}`);
}

export async function listInvestigations(): Promise<Investigation[]> {
  return apiRequest<Investigation[]>("/api/v1/investigations");
}

export async function getInvestigationStatus(id: string): Promise<Investigation> {
  return apiRequest<Investigation>(`/api/v1/investigations/${id}`);
}
