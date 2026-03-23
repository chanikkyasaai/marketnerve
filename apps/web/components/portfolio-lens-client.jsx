"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

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
  const [csvText, setCsvText] = useState("");
  const [analysis, setAnalysis] = useState(initialAnalysis);
  const [question, setQuestion] = useState("Which of my mutual funds overlap most with my direct equity holdings?");
  const [answer, setAnswer] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

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
      body: JSON.stringify({ csv_text: csvText || null, use_demo_data: !csvText.trim() }),
    }).catch(() => null);
    if (response?.ok) {
      setAnalysis(await response.json());
      setStatus("Portfolio updated.");
    } else {
      setStatus("Backend unavailable — showing demo data.");
    }
    setLoading(false);
  }

  async function runQuery() {
    setLoading(true);
    setStatus("Running portfolio reasoning…");
    const response = await fetch(`${API}/api/portfolio/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, csv_text: csvText || null, use_demo_data: !csvText.trim() }),
    }).catch(() => null);
    if (response?.ok) {
      setAnswer(await response.json());
      setStatus("Reasoning completed.");
    } else {
      setStatus("Backend unavailable.");
    }
    setLoading(false);
  }

  return (
    <div className="grid anim-fade-up">
      {/* Upload + Metrics */}
      <div className="grid cols-2">
        <article className="panel">
          <div className="section-header">
            <span className="badge badge-cyan">Upload Portfolio</span>
          </div>
          <div className="field-group" style={{ marginBottom: 12 }}>
            <label className="field-label">Paste broker / CAMS CSV</label>
            <textarea
              rows={5}
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
              placeholder="Leave empty to use demo portfolio…"
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

        {/* Stat bar for portfolio */}
        <div className="grid">
          {[
            { label: "Invested", value: `₹${Number(a?.invested_amount ?? 0).toLocaleString("en-IN")}`, tone: "" },
            { label: "Current Value", value: `₹${Number(a?.current_value ?? 0).toLocaleString("en-IN")}`, tone: "neon" },
            { label: "XIRR", value: `${((Number(a?.xirr ?? 0)) * 100).toFixed(1)}%`, tone: "neon" },
            { label: "Alpha vs NIFTY", value: `${(Number(a?.benchmark_snapshot?.relative_alpha ?? 0) * 100).toFixed(1)}%`, tone: Number(a?.benchmark_snapshot?.relative_alpha ?? 0) >= 0 ? "neon" : "red" },
          ].map((s) => (
            <article key={s.label} className="stat-card">
              <div className="stat-label">{s.label}</div>
              <div className={`stat-value ${s.tone}`} style={{ fontSize: "1.4rem" }}>{s.value}</div>
            </article>
          ))}
        </div>
      </div>

      {/* Health Score + Sector Exposure */}
      <div className="grid cols-2">
        <article className="panel corner-ornament">
          <div className="section-header">
            <span className="badge badge-neon">Money Health Score</span>
            <span style={{ fontFamily: "var(--font-display)", fontSize: "2.4rem", color: "var(--neon)", textShadow: "0 0 24px rgba(0,255,136,0.5)", marginLeft: "auto" }}>
              {health.overall ?? "—"}
              <span style={{ fontSize: "1rem", color: "var(--text3)" }}>/100</span>
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
            <span className="badge badge-cyan">Sector Exposure</span>
          </div>
          {(a?.sector_exposure ?? []).map((row) => (
            <SectorBar key={row.name} name={row.name} weight={row.weight} />
          ))}
        </article>
      </div>

      {/* Overlap Matrix + Risk Flags */}
      <div className="grid cols-2">
        <article className="panel">
          <div className="section-header">
            <span className="badge badge-amber">Fund Overlap Matrix</span>
          </div>
          <table className="war-table">
            <thead>
              <tr>
                <th>Fund</th>
                <th>Overlapping Direct Stocks</th>
              </tr>
            </thead>
            <tbody>
              {(a?.overlap_matrix ?? []).map((row) => (
                <tr key={row.fund}>
                  <td style={{ color: "var(--text)" }}>{row.fund}</td>
                  <td>
                    {row.overlaps?.length
                      ? row.overlaps.map((o) => `${o.symbol} (${(o.overlap_weight * 100).toFixed(1)}%)`).join(" · ")
                      : <span style={{ color: "var(--text3)" }}>None detected</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="panel">
          <div className="section-header">
            <span className="badge badge-red">Risk Flags</span>
          </div>
          {(a?.risk_flags ?? []).map((flag) => (
            <div key={flag} className="risk-flag">
              <span style={{ color: "var(--red)", flexShrink: 0 }}>⚠</span>
              <p>{flag}</p>
            </div>
          ))}
          <div className="section-header" style={{ marginTop: 14 }}>
            <span className="badge badge-neon">Recommended Actions</span>
          </div>
          {(a?.recommended_actions ?? []).map((act) => (
            <div key={act} className="action-item">
              <span style={{ color: "var(--neon)", flexShrink: 0 }}>→</span>
              <p>{act}</p>
            </div>
          ))}
        </article>
      </div>

      {/* Q&A */}
      <article className="panel">
        <div className="section-header">
          <span className="badge badge-purple">Portfolio Q&A Reasoning</span>
        </div>
        <div className="grid cols-2">
          <div>
            <div className="field-group" style={{ marginBottom: 10 }}>
              <label className="field-label">Ask your portfolio anything</label>
              <textarea rows={4} value={question} onChange={(e) => setQuestion(e.target.value)} />
            </div>
            <button className="war-btn full" onClick={runQuery} disabled={loading}>
              {loading ? "Reasoning…" : "Run Reasoning →"}
            </button>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
              {[
                "What is my total Reliance exposure?",
                "Which funds overlap with my stocks?",
                "What happens if RBI raises rates?",
              ].map((q) => (
                <button key={q} onClick={() => setQuestion(q)} style={{ padding: "4px 12px", background: "var(--neon-glow)", border: "1px solid var(--border2)", borderRadius: 2, color: "var(--text2)", fontFamily: "var(--font-mono)", fontSize: "0.65rem", cursor: "pointer" }}>
                  {q}
                </button>
              ))}
            </div>
          </div>

          <AnimatePresence mode="wait">
            {answer ? (
              <motion.div
                key="answer"
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                style={{ display: "grid", gap: 12 }}
              >
                <div style={{ padding: "12px 16px", border: "1px solid var(--border2)", borderRadius: "var(--r-sm)", background: "var(--neon-glow)" }}>
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.76rem", lineHeight: 1.65, color: "var(--text)" }}>{answer.answer}</p>
                </div>
                <div className="reasoning-chain">
                  {(answer.logic ?? []).map((step, i) => (
                    <div key={i} className="reasoning-step">
                      <div className="step-num">{i + 1}</div>
                      <p className="step-text">{step}</p>
                    </div>
                  ))}
                </div>
                {answer.disclaimer && (
                  <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--text3)", lineHeight: 1.5 }}>
                    ⚠ {answer.disclaimer}
                  </p>
                )}
              </motion.div>
            ) : (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
                <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--text3)", textAlign: "center", lineHeight: 1.6 }}>
                  Submit a question to run the portfolio reasoning engine.
                </p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </article>
    </div>
  );
}
