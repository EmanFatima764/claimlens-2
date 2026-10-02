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
    <main className="investigation-page">
      <section className="page-header">
        <h1>Launch Investigation</h1>
        <p>Enter a claim or piece of text to verify using our multi-agent evidence workflow.</p>
      </section>

      <div className="investigation-container">
        <div className="form-section">
          <h2>Create Investigation</h2>
          <InvestigationForm onInvestigationCreated={handleInvestigationCreated} />
        </div>

        {currentInvestigation && (
          <div className="status-section">
            <h2>Investigation Progress</h2>
            <InvestigationStatus
              investigationId={currentInvestigation.id}
              onCompleted={handleInvestigationCompleted}
            />
            {currentInvestigation.status === "completed" && (
              <div className="action-buttons">
                <a href={`/report/${currentInvestigation.id}`} className="primary-button">
                  View Full Report
                </a>
                <button
                  onClick={() => setCurrentInvestigation(null)}
                  className="secondary-button"
                >
                  Start New Investigation
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        .investigation-page {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem 1.5rem;
        }

        .page-header {
          margin-bottom: 2rem;
          text-align: center;
        }

        .page-header h1 {
          font-size: 2rem;
          margin: 0 0 0.5rem;
          color: #e2e8f0;
        }

        .page-header p {
          color: #cbd5e1;
          font-size: 1.1rem;
        }

        .investigation-container {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin-top: 2rem;
        }

        @media (max-width: 768px) {
          .investigation-container {
            grid-template-columns: 1fr;
          }
        }

        .form-section,
        .status-section {
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 16px;
          padding: 2rem;
        }

        .form-section h2,
        .status-section h2 {
          margin-top: 0;
          margin-bottom: 1.5rem;
          color: #e2e8f0;
        }

        .investigation-form {
          display: grid;
          gap: 1.5rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-weight: 600;
          color: #cbd5e1;
          font-size: 0.95rem;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
          padding: 0.75rem;
          border-radius: 8px;
          border: 1px solid rgba(148, 163, 184, 0.3);
          background: rgba(30, 41, 59, 0.8);
          color: #e2e8f0;
          font-family: inherit;
          font-size: 1rem;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-group input:disabled,
        .form-group textarea:disabled,
        .form-group select:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .error-message {
          color: #ef4444;
          font-size: 0.9rem;
          padding: 0.75rem;
          background: rgba(239, 68, 68, 0.1);
          border-radius: 8px;
          border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .submit-button {
          padding: 0.85rem;
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: opacity 0.2s;
        }

        .submit-button:hover:not(:disabled) {
          opacity: 0.9;
        }

        .submit-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .investigation-status {
          padding: 1.5rem;
          background: rgba(30, 41, 59, 0.5);
          border-left: 4px solid #2563eb;
          border-radius: 8px;
        }

        .status-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .status-header h3 {
          margin: 0;
          color: #e2e8f0;
        }

        .status-badge {
          padding: 0.35rem 0.75rem;
          border-radius: 20px;
          color: white;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .status-details {
          margin: 1rem 0;
          font-size: 0.9rem;
          color: #cbd5e1;
        }

        .status-details p {
          margin: 0.5rem 0;
        }

        .polling-indicator {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-top: 1rem;
          color: #f59e0b;
          font-size: 0.9rem;
        }

        .spinner {
          display: inline-block;
          width: 16px;
          height: 16px;
          border: 2px solid rgba(245, 158, 11, 0.3);
          border-top-color: #f59e0b;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        .verdict-preview {
          margin-top: 1rem;
          padding: 1rem;
          background: rgba(16, 185, 129, 0.1);
          border: 1px solid rgba(16, 185, 129, 0.3);
          border-radius: 8px;
        }

        .verdict-label {
          margin: 0;
          color: #10b981;
        }

        .error-details {
          margin-top: 1rem;
          padding: 1rem;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 8px;
        }

        .error-text {
          margin: 0;
          color: #ef4444;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .primary-button,
        .secondary-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          text-decoration: none;
          padding: 0.75rem 1.2rem;
          border-radius: 8px;
          font-weight: 600;
          border: none;
          cursor: pointer;
          transition: opacity 0.2s;
        }

        .primary-button {
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
        }

        .secondary-button {
          background: rgba(148, 163, 184, 0.12);
          color: #e2e8f0;
          border: 1px solid rgba(148, 163, 184, 0.2);
        }

        .primary-button:hover,
        .secondary-button:hover {
          opacity: 0.9;
        }
      `}</style>
    </main>
  );
}
