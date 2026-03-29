import { MarketNerveShell, PatternCard } from "../../components/marketnerve-shell";
import { getPatternsData, getHealthData } from "../../lib/marketnerve-api.mjs";

const PATTERN_TYPES = ["Golden Cross", "Death Cross", "RSI Oversold Bounce", "RSI Overbought", "Volume Surge Breakout", "52-Week High", "52-Week Low Support", "Bollinger Squeeze", "Cup & Handle", "Double Bottom"];
const SECTORS = ["Information Technology", "Financial Services", "Consumer Discretionary", "Energy", "Healthcare"];

export default async function PatternsPage({ searchParams }) {
  const params = await searchParams;
  const [patterns, health] = await Promise.all([
    getPatternsData({
      patternType: params?.pattern_type || "",
      ticker: params?.ticker || "",
    }),
    getHealthData(),
  ]);

  const highConv = patterns.filter((p) => (p.confidence ?? 0) >= 0.75);
  const avgWinRate = patterns.length
    ? (patterns.reduce((a, p) => a + (p.backtest?.win_rate ?? p.win_rate ?? 0), 0) / patterns.length * 100).toFixed(0)
    : 0;

  return (
    <MarketNerveShell
      marketStatus={health.market_status}
      eyebrow="Pattern Intelligence · Technical Analysis"
      title={`Pattern <span class="accent2">Hub</span>`}
      subtitle="Real-time technical pattern detection across NSE — back-tested win rates, R/R ratios, and risk context"
    >
      {/* Quick stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { label: "Patterns Detected", value: patterns.length, color: "var(--text)" },
          { label: "High Conviction", value: highConv.length, color: "var(--cyan)" },
          { label: "Avg Win Rate", value: `${avgWinRate}%`, color: "var(--green)" },
        ].map((s) => (
          <div key={s.label} className="panel" style={{ padding: "14px 18px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</span>
            <span style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: "20px", color: s.color, letterSpacing: "-0.02em" }}>{s.value}</span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <article className="panel" style={{ marginBottom: 20, padding: "16px 20px" }}>
        <form className="filters-bar" action="/patterns" method="get">
          <div className="field-group">
            <label className="field-label">Pattern Type</label>
            <select name="pattern_type" defaultValue={params?.pattern_type || ""} style={{
              height: 36, padding: "0 12px", background: "var(--surface-2)", border: "1px solid var(--border)",
              borderRadius: 8, color: "var(--text)", fontSize: 14, outline: "none", minWidth: 200
            }}>
              <option value="">All Patterns</option>
              {PATTERN_TYPES.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="field-group">
            <label className="field-label">Ticker</label>
            <input name="ticker" defaultValue={params?.ticker || ""} placeholder="e.g. HDFCBANK" style={{ width: 140 }} />
          </div>
          <button type="submit" className="war-btn cyan">Scan →</button>
          {(params?.pattern_type || params?.ticker) && (
            <a href="/patterns" style={{ height: 36, padding: "0 14px", display: "flex", alignItems: "center", fontSize: 13, color: "var(--text-3)", textDecoration: "none", border: "1px solid var(--border)", borderRadius: 8, fontFamily: "var(--font-mono)" }}>Clear</a>
          )}
        </form>
      </article>

      {/* Pattern win-rate legend */}
      <div style={{ display: "flex", gap: 16, marginBottom: 16, paddingBottom: 12, borderBottom: "1px solid var(--border)" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)" }}>
          {patterns.length} patterns · sorted by confidence
        </span>
        <div style={{ display: "flex", gap: 12, marginLeft: "auto" }}>
          {[["≥75% conf", "var(--green)"], ["≥60%", "var(--amber)"], ["<60%", "var(--text-3)"]].map(([label, color]) => (
            <span key={label} style={{ display: "flex", alignItems: "center", gap: 4, fontFamily: "var(--font-mono)", fontSize: "11px", color }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: color, display: "inline-block" }} />
              {label}
            </span>
          ))}
        </div>
      </div>

      <div className="grid cols-2">
        {patterns.map((p, i) => <PatternCard key={`${p.ticker}-${p.pattern_type}`} pattern={p} index={i} />)}
      </div>

      {patterns.length === 0 && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "var(--text-3)" }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>◈</div>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: 13 }}>No patterns match your filters</p>
          <a href="/patterns" style={{ display: "inline-block", marginTop: 12, fontSize: 12, color: "var(--cyan)", fontFamily: "var(--font-mono)" }}>Clear filters</a>
        </div>
      )}
    </MarketNerveShell>
  );
}
