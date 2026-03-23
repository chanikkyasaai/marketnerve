"use client";

import { useState } from "react";

export function PortfolioLensClient({ initialAnalysis }) {
  const [csvText, setCsvText] = useState("");
  const [analysis, setAnalysis] = useState(initialAnalysis);
  const [question, setQuestion] = useState("Which of my mutual funds overlap most with my direct equity holdings?");
  const [answer, setAnswer] = useState(null);
  const [status, setStatus] = useState("");

  async function analyzePortfolio() {
    setStatus("Analyzing portfolio...");
    setAnswer(null);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/portfolio/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        csv_text: csvText || null,
        use_demo_data: !csvText.trim(),
      }),
    }).catch(() => null);

    if (!response?.ok) {
      setStatus("Backend unavailable. Showing the current demo analysis.");
      return;
    }

    const payload = await response.json();
    setAnalysis(payload);
    setStatus("Portfolio analysis updated.");
  }

  async function askQuestion() {
    setStatus("Running portfolio reasoning...");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/portfolio/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        csv_text: csvText || null,
        use_demo_data: !csvText.trim(),
      }),
    }).catch(() => null);

    if (!response?.ok) {
      setStatus("Backend unavailable. Query result could not be refreshed.");
      return;
    }

    const payload = await response.json();
    setAnswer(payload);
    setStatus("Portfolio reasoning completed.");
  }

  return (
    <div className="grid">
      <section className="panel">
        <div className="filters-grid">
          <label className="wide-field">
            Upload broker/CAMS CSV text
            <textarea
              rows="8"
              value={csvText}
              onChange={(event) => setCsvText(event.target.value)}
              placeholder="Paste CSV rows here, or leave empty to use the demo portfolio."
            />
          </label>
          <button type="button" onClick={analyzePortfolio}>Analyze portfolio</button>
        </div>
        {status ? <p className="subtle">{status}</p> : null}
      </section>

      <section className="metric-row">
        <article className="metric-card">
          <span>Invested</span>
          <strong>₹{Number(analysis.invested_amount).toLocaleString("en-IN")}</strong>
        </article>
        <article className="metric-card tone-positive">
          <span>Current</span>
          <strong>₹{Number(analysis.current_value).toLocaleString("en-IN")}</strong>
        </article>
        <article className="metric-card tone-positive">
          <span>XIRR</span>
          <strong>{(Number(analysis.xirr) * 100).toFixed(2)}%</strong>
        </article>
        <article className="metric-card">
          <span>Money Health Score</span>
          <strong>{analysis.money_health_score}</strong>
        </article>
      </section>

      <section className="split">
        <article className="panel">
          <h2>Portfolio X-Ray</h2>
          <div className="grid">
            <div>
              <p className="chip">Sector Exposure</p>
              <div className="tags">
                {analysis.sector_exposure.map((row) => (
                  <span key={row.sector}>
                    {row.sector}: {(row.weight * 100).toFixed(1)}%
                  </span>
                ))}
              </div>
            </div>
            <div>
              <p className="chip amber">Recommended Actions</p>
              <div className="timeline">
                {analysis.recommended_actions.map((item) => (
                  <div className="timeline-item" key={item}>
                    <strong>Action</strong>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </article>
        <article className="panel">
          <p className="chip">Portfolio Q&A</p>
          <label className="wide-field">
            Ask a question
            <textarea rows="4" value={question} onChange={(event) => setQuestion(event.target.value)} />
          </label>
          <button type="button" onClick={askQuestion}>Run reasoning</button>
          {answer ? (
            <div className="timeline">
              <div className="timeline-item">
                <strong>Answer</strong>
                <span>{answer.answer}</span>
              </div>
              {answer.logic.map((step) => (
                <div className="timeline-item" key={step}>
                  <strong>Logic</strong>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          ) : null}
        </article>
      </section>

      <section className="panel">
        <h2>Overlap Matrix</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Fund</th>
              <th>Overlapping Symbols</th>
            </tr>
          </thead>
          <tbody>
            {analysis.overlap_matrix.map((row) => (
              <tr key={row.fund}>
                <td>{row.fund}</td>
                <td>
                  {row.overlaps.length
                    ? row.overlaps.map((item) => `${item.symbol} (${(item.overlap_weight * 100).toFixed(1)}%)`).join(", ")
                    : "No direct overlap"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
