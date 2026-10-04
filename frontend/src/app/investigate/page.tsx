"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Investigation } from "@/types/investigation";
import InvestigationForm from "@/components/investigation/InvestigationForm";
import InvestigationStatus from "@/components/investigation/InvestigationStatus";

export default function InvestigationPage() {
  const router = useRouter();
  const [currentInvestigation, setCurrentInvestigation] = useState<Investigation | null>(null);

  const handleInvestigationCreated = (investigation: Investigation) => {
    setCurrentInvestigation(investigation);
  };

  const handleInvestigationCompleted = (investigation: Investigation) => {
    setCurrentInvestigation(investigation);
    // As soon as the agents finish, show the evidence and the most likely answer.
    if (investigation.status === "completed") router.push(`/report/${investigation.id}`);
  };

  return (
    <main className="investigation-shell">
      <div className="section-header">
        <div>
          <span className="eyebrow">Evidence workflow</span>
          <h1 style={{ marginTop: "0.9rem", fontSize: "clamp(2rem, 4vw, 3rem)" }}>Check a claim</h1>
          <p>Enter a claim. Agents will find sources, extract the evidence and give the most likely answer.</p>
        </div>
      </div>

      <div className="investigation-grid">
        <section className="glass-section">
          <h2 style={{ marginTop: 0, marginBottom: "1.2rem" }}>Your claim</h2>
          <InvestigationForm onInvestigationCreated={handleInvestigationCreated} />
        </section>

        {currentInvestigation ? (
          <section className="glass-section" style={{ display: "grid", gap: "1rem" }}>
            <h2 style={{ margin: 0 }}>Progress</h2>
            <InvestigationStatus
              investigationId={currentInvestigation.id}
              onCompleted={handleInvestigationCompleted}
            />
            {(currentInvestigation.status === "completed" || currentInvestigation.status === "failed") && (
              <div className="actions" style={{ marginTop: 0 }}>
                {currentInvestigation.status === "completed" && (
                  <a href={`/report/${currentInvestigation.id}`} className="primary-button">
                    View evidence
                  </a>
                )}
                <button onClick={() => setCurrentInvestigation(null)} className="secondary-button">
                  Check another claim
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
            <div className="workflow-step step-one"><span>01</span><strong>Claim</strong><small>Extract the claim</small></div>
            <div className="workflow-step step-two"><span>02</span><strong>Research</strong><small>Search the web</small></div>
            <div className="workflow-step step-three"><span>03</span><strong>Sources</strong><small>Score credibility</small></div>
            <div className="workflow-step step-four"><span>04</span><strong>Evidence</strong><small>Most likely answer</small></div>
            <div className="preview-footer"><span>Four agents</span><span className="preview-line" /><span>Evidence + most likely answer</span></div>
          </section>
        )}
      </div>
    </main>
  );
}
