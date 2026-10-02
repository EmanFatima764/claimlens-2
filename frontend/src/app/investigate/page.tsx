export default function InvestigatePage() {
  return (
    <main style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <h1>Investigate</h1>
      <p>Launch a new evidence investigation workflow.</p>
      <form style={{ display: "grid", gap: "1rem" }}>
        <textarea
          placeholder="Paste a claim, a URL, or a document summary..."
          rows={8}
          style={{ width: "100%", padding: "1rem", borderRadius: "12px", border: "1px solid #cbd5e1" }}
        />
        <button type="button" style={{ width: "fit-content", padding: "0.8rem 1.2rem", borderRadius: "10px", border: "none", background: "#2563eb", color: "white" }}>
          Start workflow
        </button>
      </form>
    </main>
  );
}
