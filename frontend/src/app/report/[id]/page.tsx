export default function ReportPage({ params }: { params: { id: string } }) {
  return (
    <main style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <h1>Evidence Report</h1>
      <p>Report ID: {params.id}</p>
      <p>Placeholder report page for final verdict and evidence output.</p>
    </main>
  );
}
