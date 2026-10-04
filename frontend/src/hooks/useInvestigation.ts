import type { InvestigationSummary } from "@/types";

export function useInvestigation() {
  return {
    loading: false,
    investigation: null as InvestigationSummary | null,
  };
}
