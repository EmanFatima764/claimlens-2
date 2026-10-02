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
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [sourceType, setSourceType] = useState<"text" | "url" | "pdf" | "audio">("text");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const investigation = await createInvestigation({
        title,
        description,
        source_type: sourceType,
      });

      if (onInvestigationCreated) {
        onInvestigationCreated(investigation);
      }

      // Clear form
      setTitle("");
      setDescription("");
      setSourceType("text");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create investigation");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="investigation-form">
      <div className="form-group">
        <label htmlFor="title">Investigation Title</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g., Verify startup metrics claim"
          required
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Claim or Input Text</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Paste the claim you want to fact-check..."
          rows={8}
          required
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="sourceType">Input Type</label>
        <select
          id="sourceType"
          value={sourceType}
          onChange={(e) => setSourceType(e.target.value as any)}
          disabled={isLoading}
        >
          <option value="text">Text</option>
          <option value="url">URL</option>
          <option value="pdf">PDF</option>
          <option value="audio">Audio</option>
        </select>
      </div>

      {error && <div className="error-message">{error}</div>}

      <button type="submit" disabled={isLoading} className="submit-button">
        {isLoading ? "Starting Investigation..." : "Start Investigation"}
      </button>
    </form>
  );
}
