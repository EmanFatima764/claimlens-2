import "./globals.css";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Agentic Evidence Intelligence Platform</p>
        <h1>ClaimLens 2.0</h1>
        <p className="subtitle">
          Multi-agent claim verification, evidence collection, conflict analysis, and uncertainty-aware verdicting.
        </p>
        <div className="actions">
          <a href="/investigate" className="primary-button">Start Investigation</a>
          <a href="/report/sample" className="secondary-button">View Sample Report</a>
        </div>
      </section>

      <section className="grid">
        <div className="card">
          <h2>Supported Inputs</h2>
          <ul>
            <li>Text claims</li>
            <li>URLs</li>
            <li>PDF uploads</li>
            <li>Short audio</li>
          </ul>
        </div>
        <div className="card">
          <h2>Workflow</h2>
          <ul>
            <li>Claim extraction</li>
            <li>Research and source quality</li>
            <li>Evidence verification</li>
            <li>Conflict and graph analysis</li>
            <li>Final verdict</li>
          </ul>
        </div>
        <div className="card">
          <h2>Agent Stack</h2>
          <ul>
            <li>Claim Agent</li>
            <li>Research Agent</li>
            <li>Source Agent</li>
            <li>Evidence Agent</li>
            <li>Verdict Agent</li>
          </ul>
        </div>
      </section>
    </main>
  );
}
