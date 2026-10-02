"use client";

import { useEffect, useState } from "react";
import { Investigation } from "@/types/investigation";
import { getInvestigationStatus } from "@/lib/investigations";

interface InvestigationStatusProps {
  investigationId: string;
  onCompleted?: (investigation: Investigation) => void;
}

export default function InvestigationStatus({
  investigationId,
  onCompleted,
}: InvestigationStatusProps) {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pollCount, setPollCount] = useState(0);

  useEffect(() => {
    if (!investigationId) return;

    async function fetchStatus() {
      try {
        const data = await getInvestigationStatus(investigationId);
        setInvestigation(data);
        setError(null);

        // Stop polling if investigation is complete or failed
        if (data.status === "completed" || data.status === "failed") {
          if (onCompleted) {
            onCompleted(data);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch status");
      } finally {
        setIsLoading(false);
      }
    }

    // Initial fetch
    fetchStatus();

    // Poll every 2 seconds if still running
    const interval = setInterval(() => {
      if (investigation?.status === "running" || investigation?.status === "draft") {
        fetchStatus();
        setPollCount((c) => c + 1);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [investigationId, investigation?.status, onCompleted]);

  if (isLoading && !investigation) {
    return <div className="status-loading">Loading investigation status...</div>;
  }

  if (error) {
    return <div className="status-error">Error: {error}</div>;
  }

  if (!investigation) {
    return <div className="status-error">Investigation not found</div>;
  }

  const statusColors: Record<Investigation["status"], string> = {
    draft: "#64748b",
    running: "#f59e0b",
    completed: "#10b981",
    failed: "#ef4444",
  };

  return (
    <div className="investigation-status" style={{ borderLeftColor: statusColors[investigation.status] }}>
      <div className="status-header">
        <h3>{investigation.title}</h3>
        <span className="status-badge" style={{ backgroundColor: statusColors[investigation.status] }}>
          {investigation.status.toUpperCase()}
        </span>
      </div>

      <div className="status-details">
        <p>
          <strong>ID:</strong> {investigation.id}
        </p>
        <p>
          <strong>Source Type:</strong> {investigation.source_type || "text"}
        </p>
        {investigation.workflow_status && (
          <p>
            <strong>Workflow:</strong> {investigation.workflow_status}
          </p>
        )}
      </div>

      {investigation.status === "running" && (
        <div className="polling-indicator">
          <span className="spinner"></span>
          Polling for updates... (Request #{pollCount})
        </div>
      )}

      {investigation.status === "completed" && investigation.final_verdict && (
        <div className="verdict-preview">
          <p className="verdict-label">
            <strong>Verdict:</strong> {JSON.stringify(investigation.final_verdict)}
          </p>
        </div>
      )}

      {investigation.status === "failed" && investigation.error && (
        <div className="error-details">
          <p className="error-text">{investigation.error}</p>
        </div>
      )}
    </div>
  );
}
