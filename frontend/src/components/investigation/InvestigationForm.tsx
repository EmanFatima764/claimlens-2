"use client";

import { useState } from "react";
import { Investigation } from "@/types/investigation";
import { createInvestigation } from "@/lib/investigations";

interface InvestigationFormProps {
  onInvestigationCreated?: (investigation: Investigation) => void;
}

export default function InvestigationForm({
  onInvestigationCreated,
}: InvestigationFormProps) {
  const [claim, setClaim] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const text = claim.trim();
      const investigation = await createInvestigation({
        title: text.replace(/\s+/g, " ").slice(0, 80),
        input_text: text,
        source_type: "text",
      });

      if (onInvestigationCreated) {
        onInvestigationCreated(investigation);
      }

      setClaim("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create investigation");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="investigation-form">
      <div className="form-group">
        <label htmlFor="claim">Claim to check</label>
        <textarea
          id="claim"
          value={claim}
          onChange={(e) => setClaim(e.target.value)}
          placeholder="e.g., Donald Trump is the president of the USA"
          rows={5}
          required
          disabled={isLoading}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <button type="submit" disabled={isLoading} className="submit-button">
        {isLoading ? "Starting..." : "Check this claim"}
      </button>
    </form>
  );
}
