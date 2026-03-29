"use client";
import { motion } from "framer-motion";
import { useRef, useState } from "react";

function HealthRing({ score, label, size = 60, color = "var(--neon)" }) {
  const r = (size / 2) - 6;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
      <div style={{ position: "relative", width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(0,255,136,0.08)" strokeWidth="5" />
          <circle
            cx={size / 2} cy={size / 2} r={r}
            fill="none"
            stroke={color}
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circ - dash}`}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
            style={{ filter: `drop-shadow(0 0 4px ${color})` }}
          />
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--font-mono)", fontSize: "0.75rem", fontWeight: 700, color }}>
          {score}
        </div>
      </div>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.55rem", color: "var(--text3)", textTransform: "uppercase", letterSpacing: "0.1em", textAlign: "center", width: size }}>
        {label}
      </span>
    </div>
  );
}

function SectorBar({ name, weight }) {
  const pct = Math.round(weight * 100);
  return (
    <div>
      <div className="progress-row">
        <span className="progress-name">{name}</span>
        <span className="progress-pct">{pct}%</span>
      </div>
      <div className="progress-track">
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

export function PortfolioLensClient({ initialAnalysis }) {
  const fileInputRef = useRef(null);
  const [csvText, setCsvText] = useState("");
  const [analysis, setAnalysis] = useState(initialAnalysis || null);
  const [question, setQuestion] = useState("Which of my mutual funds overlap most with my direct equity holdings?");
  const [answer, setAnswer] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState("");

  const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const a = analysis;
  const health = a?.money_health_score ?? {};

  async function runAnalyze() {
    setLoading(true);
    setStatus("Running portfolio analysis…");
    setAnswer(null);
    const response = await fetch(`${API}/api/portfolio/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ csv_text: csvText || null, use_demo_data: false }),
    }).catch(() => null);
    if (response?.ok) {
      setAnalysis(await response.json());
      setStatus("Portfolio updated.");
    } else {
      setStatus("Backend unavailable.");
    }
    setLoading(false);
  }

  async function runQuery() {
    setLoading(true);
    setStatus("Running portfolio reasoning…");
    const response = await fetch(`${API}/api/portfolio/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, csv_text: csvText || null, use_demo_data: false }),
    }).catch(() => null);
    if (response?.ok) {
      setAnswer(await response.json());
      setStatus("Reasoning completed.");
    } else {
      setStatus("Backend unavailable.");
    }
    setLoading(false);
  }

  function onSelectCsvClick() {
    fileInputRef.current?.click();
  }

  async function onCsvFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setStatus("Please choose a .csv file.");
      return;
    }

    try {
      const text = await file.text();
      setCsvText(text);
      setSelectedFileName(file.name);
      setStatus(`Loaded ${file.name}`);
    } catch {
      setStatus("Could not read the selected file.");
    }
  }

  return (
    <div className="grid anim-fade-up">
      {/* Upload section */}
      <article className="panel">
        <div className="section-header">
          <span className="badge badge-cyan">Upload Portfolio</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,text/csv"
            onChange={onCsvFileChange}
            style={{ display: "none" }}
          />
          <button type="button" className="war-btn cyan" onClick={onSelectCsvClick} disabled={loading}>
            Choose CSV File
          </button>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.68rem", color: "var(--text3)" }}>
            {selectedFileName || "No file selected"}
          </span>
        </div>
        <div className="field-group" style={{ marginBottom: 12 }}>
          <label className="field-label">Paste CSV (Format: Symbol,Name,InvestedValue,CurrentValue)</label>
          <textarea
            rows={5}
            value={csvText}
            onChange={(e) => setCsvText(e.target.value)}
            placeholder="RELIANCE,Reliance,3500000,4200000
HDFCBANK,HDFC Bank,2500000,3100000
TCS,TCS,1875000,2250000"
          />
        </div>
        <button className="war-btn full cyan" onClick={runAnalyze} disabled={loading}>
          {loading ? "Processing…" : "Analyze Portfolio"}
        </button>
        {status && (
          <p style={{ marginTop: 10, fontFamily: "var(--font-mono)", fontSize: "0.68rem", color: "var(--text3)" }}>
            {status}
          </p>
        )}
      </article>

      {/* Stats */}
      {a && (
        <div className="grid cols-2">
          <article className="stat-card">
            <div className="stat-label">Invested</div>
            <div className="stat-value">{`₹${Number(a?.invested_amount ?? 0).toLocaleString("en-IN")}`}</div>
          </article>
          <article className="stat-card">
            <div className="stat-label">Current Value</div>
            <div className="stat-value">{`₹${Number(a?.current_value ?? 0).toLocaleString("en-IN")}`}</div>
          </article>
          <article className="stat-card">
            <div className="stat-label">XIRR</div>
            <div className="stat-value">{`${((Number(a?.xirr ?? 0)) * 100).toFixed(1)}%`}</div>
          </article>
          <article className="stat-card">
            <div className="stat-label">Alpha vs NIFTY</div>
            <div className="stat-value">{`${(Number(a?.benchmark_snapshot?.relative_alpha ?? 0) * 100).toFixed(1)}%`}</div>
          </article>
        </div>
      )}

      {/* Health + Sector */}
      {a && (
        <div className="grid cols-2">
          <article className="panel corner-ornament">
            <div className="section-header">
              <span className="badge badge-neon">Money Health Score</span>
              <span style={{ fontFamily: "var(--font-display)", fontSize: "2.4rem", color: "var(--neon)", textShadow: "0 0 24px rgba(0,255,136,0.5)", marginLeft: "auto" }}>
                {health.overall ?? "—"}
              </span>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 14, justifyContent: "center", padding: "10px 0" }}>
              {[
                ["Diversification", health.diversification, "var(--neon)"],
                ["Momentum", health.momentum_alignment, "var(--neon2)"],
                ["Concentration", health.concentration_risk, "var(--amber)"],
                ["Profit Quality", health.profit_quality, "var(--neon)"],
                ["Downside Res.", health.downside_resilience, "var(--neon2)"],
                ["Liquidity", health.liquidity_buffer, "var(--amber)"],
              ].filter(([, v]) => v != null).map(([l, v, c]) => (
                <HealthRing key={l} score={v} label={l} size={68} color={c} />
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="section-header">
              <span className="badge badge-amber">Sector Exposure</span>
            </div>
            <div style={{ display: "grid", gap: 14 }}>
              {(a?.sector_exposure ?? []).map((s) => <SectorBar key={s.name} name={s.name} weight={s.weight} />)}
            </div>
          </article>
        </div>
      )}

      {/* Holdings */}
      {a && (
        <article className="panel">
          <div className="section-header">
            <span className="badge">Holdings</span>
            <span className="section-count">{a.holdings_count}</span>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table className="war-table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Name</th>
                  <th>Qty</th>
                  <th>Invested</th>
                  <th>Current</th>
                  <th>Weight</th>
                </tr>
              </thead>
              <tbody>
                {(a?.holdings ?? []).map((h) => (
                  <tr key={h.ticker}>
                    <td>{h.ticker}</td>
                    <td>{h.name}</td>
                    <td>{h.qty || "—"}</td>
                    <td>₹{Number(h.invested || 0).toLocaleString()}</td>
                    <td>₹{Number(h.current_value || 0).toLocaleString()}</td>
                    <td>{Math.round((h.weight || 0) * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      )}

      {/* Q&A */}
      {a && (
        <article className="panel">
          <div className="section-header">
            <span className="badge badge-neon">Ask Your Portfolio</span>
          </div>
          <div className="field-group" style={{ marginBottom: 10 }}>
            <textarea rows={3} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about your portfolio..." />
          </div>
          <button className="war-btn full" onClick={runQuery} disabled={loading}>
            {loading ? "Reasoning…" : "Run Reasoning"}
          </button>
          {answer && (
            <div style={{ marginTop: 14, padding: 12, background: "rgba(0,255,136,0.05)", borderRadius: 6 }}>
              <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.6, color: "var(--text)" }}>
                {answer.answer}
              </p>
            </div>
          )}
        </article>
      )}
    </div>
  );
}
