export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let detail = "";
    try {
      const body = await response.json();
      detail = typeof body?.detail === "string" ? body.detail : JSON.stringify(body?.detail ?? "");
    } catch {
      /* body was not JSON */
    }
    throw new ApiError(`Request failed (${response.status})${detail ? `: ${detail}` : ""}`, response.status);
  }

  return (await response.json()) as T;
}

export async function getHealth() {
  return apiRequest<{ status: string; database?: string; llm_configured?: boolean; tavily_configured?: boolean }>(
    "/api/v1/health"
  );
}
