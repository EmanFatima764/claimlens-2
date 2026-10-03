"use client";

import { useState } from "react";
import { Investigation } from "@/types/investigation";
import InvestigationForm from "@/components/investigation/InvestigationForm";
import InvestigationStatus from "@/components/investigation/InvestigationStatus";

export default function InvestigationPage() {
  const [currentInvestigation, setCurrentInvestigation] = useState<Investigation | null>(null);

  const handleInvestigationCreated = (investigation: Investigation) => {
    setCurrentInvestigation(investigation);
  };

  const handleInvestigationCompleted = (investigation: Investigation) => {
    setCurrentInvestigation(investigation);
  };

  return (
    <main className="investigation-shell">
      <div className="section-header">
        <div>
          <span className="eyebrow">Evidence workflow</span>
          <h1 style={{ marginTop: "0.9rem", fontSize: "clamp(2rem, 4vw, 3rem)" }}>Launch investigation</h1>
          <p>Run a claim through research, evidence extraction, and verdict synthesis.</p>
        </div>
      </div>

      <div className="investigation-grid">
        <section className="glass-section">
          <h2 style={{ marginTop: 0, marginBottom: "1.2rem" }}>Create investigation</h2>
          <InvestigationForm onInvestigationCreated={handleInvestigationCreated} />
        </section>

        {currentInvestigation ? (
          <section className="glass-section" style={{ display: "grid", gap: "1rem" }}>
            <h2 style={{ margin: 0 }}>Investigation progress</h2>
            <InvestigationStatus
              investigationId={currentInvestigation.id}
              onCompleted={handleInvestigationCompleted}
            />
            {currentInvestigation.status === "completed" && (
              <div className="actions" style={{ marginTop: 0 }}>
                <a href={`/report/${currentInvestigation.id}`} className="primary-button">
                  View full report
                </a>
                <button onClick={() => setCurrentInvestigation(null)} className="secondary-button">
                  Start new investigation
                </button>
              </div>
            )}
          </section>
        ) : (
          <section className="workflow-preview" aria-label="Investigation workflow preview">
            <div className="workflow-orbit orbit-one" />
            <div className="workflow-orbit orbit-two" />
            <div className="preview-heading">
              <span className="mini-tag">Your verification runway</span>
              <span className="preview-live"><span /> Ready to analyze</span>
            </div>
            <div className="workflow-core">
              <span className="core-ring" />
              <strong>Claim<br />signal</strong>
            </div>
            <div className="workflow-step step-one"><span>01</span><strong>Extract</strong><small>Define the claim</small></div>
            <div className="workflow-step step-two"><span>02</span><strong>Research</strong><small>Find primary sources</small></div>
            <div className="workflow-step step-three"><span>03</span><strong>Verify</strong><small>Map evidence</small></div>
            <div className="workflow-step step-four"><span>04</span><strong>Verdict</strong><small>Explain confidence</small></div>
            <div className="preview-footer"><span>Four stages</span><span className="preview-line" /><span>One transparent answer</span></div>
          </section>
        )}
      </div>
    </main>
  );
}
