import "./globals.css";

const featureCards = [
  {
    title: "Multi-source verification",
    items: ["Claim extraction", "Web research", "Source quality scoring", "Evidence validation"],
  },
  {
    title: "Decision intelligence",
    items: ["Credibility ranking", "Source-linked evidence", "Conflict detection", "Confidence & uncertainty"],
  },
  {
    title: "Agentic workflow",
    items: ["Claim, Research, Source", "Evidence Agent", "Conflict Agent", "Verdict Agent"],
  },
];

export default function HomePage() {
  return (
    <main className="page-shell">
      <span className="ambient-orb one" />
      <span className="ambient-orb two" />

      <section className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">Agentic evidence intelligence</span>
          <h1>
            Verify claims with <span>clarity</span> and confidence.
          </h1>
          <p className="subtitle">
            ClaimLens 2.0 turns raw claims into transparent, source-linked evidence and a most likely answer using a multi-agent workflow built for fact-checking, research synthesis, and trust analysis.
          </p>

          <div className="actions">
            <a href="/investigate" className="primary-button">Start investigation</a>
            <a href="/report/sample" className="secondary-button">View sample report</a>
          </div>

          <div className="stat-row">
            <div className="stat-card">
              <strong>6</strong>
              <span>Specialist agents</span>
            </div>
            <div className="stat-card">
              <strong>Live</strong>
              <span>Web research</span>
            </div>
            <div className="stat-card">
              <strong>Every</strong>
              <span>claim source-linked</span>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="visual-stack">
            <div className="floating-panel main">
              <span className="mini-tag">Live signal</span>
              <h2 style={{ margin: "1rem 0 0.75rem", fontSize: "1.6rem" }}>Claim verdict</h2>

              <div className="metric-line">
                <div className="metric-row">
                  <span>Verdict</span>
                  <span className="pill success">Mostly true</span>
                </div>
                <div className="metric-row">
                  <span>Confidence</span>
                  <strong>86%</strong>
                </div>
                <div className="metric-row">
                  <span>Uncertainty</span>
                  <strong>12%</strong>
                </div>
              </div>
            </div>

            <div className="floating-panel side">
              <div className="metric-row">
                <span>Sources</span>
                <span className="pill neutral">26</span>
              </div>
              <div className="metric-row">
                <span>Conflicts</span>
                <span className="pill neutral">3</span>
              </div>
            </div>

            <div className="floating-panel bottom">
              <div className="metric-row">
                <span>Review</span>
                <span className="pill success">No</span>
              </div>
              <div className="metric-row">
                <span>Risk</span>
                <span className="pill neutral">Low</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid">
        {featureCards.map((card) => (
          <div key={card.title} className="card">
            <h2>{card.title}</h2>
            <ul>
              {card.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </main>
  );
}
