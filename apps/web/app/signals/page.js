import { MarketNerveShell, SignalCard } from "../../components/marketnerve-shell";
import { getSignalsData, getHealthData, getSignalsPerformance, getSignalsCalibration } from "../../lib/marketnerve-api.mjs";

const SECTORS = ["Information Technology", "Financial Services", "Consumer Discretionary", "Energy", "Healthcare", "Industrials"];
const SIGNAL_TYPES = ["Insider Trade", "FII Accumulation", "Volume Anomaly", "Momentum Surge", "Bulk Deal", "Corporate Filing"];

export default async function SignalsPage({ searchParams }) {
  const params = await searchParams;
  const [signals, health, performance, calibration] = await Promise.all([
    getSignalsData({
      sector: params?.sector || "",
      minConfidence: params?.min_confidence || "",
    }),
    getHealthData(),
    getSignalsPerformance(),
    getSignalsCalibration(),
  ]);

  const highConf = signals.filter((s) => (s.confidence ?? 0) >= 0.8);
  const avgConf = signals.length ? (signals.reduce((a, s) => a + (s.confidence ?? 0), 0) / signals.length * 100).toFixed(0) : 0;

  return (
    <MarketNerveShell
      marketStatus={health.market_status}
      eyebrow="Signal Scout · NSE Filing Intelligence"
      title={`Signal <span class="accent">Radar</span>`}
      subtitle="Source-cited · Z-scored anomaly detection · Back-tested · Full audit trail"
    >
      {/* Quick stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { label: "Total Signals", value: signals.length, color: "var(--text)" },
          { label: "High Conviction", value: highConf.length, color: "var(--green)" },
          { label: "Avg Confidence", value: `${avgConf}%`, color: "var(--accent)" },
        ].map((s) => (
          <div key={s.label} className="panel" style={{ padding: "14px 18px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</span>
            <span style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: "20px", color: s.color, letterSpacing: "-0.02em" }}>{s.value}</span>
          </div>
        ))}
      </div>

      {/* Performance tracker */}
      <article className="panel" style={{ marginBottom: 20, padding: "16px 20px" }}>
        <div className="section-header" style={{ marginBottom: 12 }}>
          <span className="badge badge-neon">Performance Tracker</span>
          <span className="section-count">Sample: {performance.sample_size}</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 12 }}>
          {[
            ["T+1", performance?.horizons?.t1],
            ["T+5", performance?.horizons?.t5],
            ["T+30", performance?.horizons?.t30],
          ].map(([label, value]) => (
            <div key={label} style={{ padding: "10px 12px", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface-1)" }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>
                {label} Expected Return
              </div>
              <div style={{ fontFamily: "var(--font-ui)", fontWeight: 800, fontSize: 20, color: Number(value) >= 0 ? "var(--green)" : "var(--red)", letterSpacing: "-0.02em" }}>
                {`${Number(value || 0) >= 0 ? "+" : ""}${(Number(value || 0) * 100).toFixed(2)}%`}
              </div>
            </div>
          ))}
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          {(performance.by_signal_type || []).slice(0, 4).map((row) => (
            <div key={row.signal_type} style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 8, padding: "8px 10px", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface-0)" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-2)" }}>{row.signal_type}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-3)" }}>{`${(Number(row.t1_return) * 100).toFixed(2)}%`}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-3)" }}>{`${(Number(row.t5_return) * 100).toFixed(2)}%`}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-3)" }}>{`${(Number(row.t30_return) * 100).toFixed(2)}%`}</span>
            </div>
          ))}
        </div>
      </article>

      {/* Confidence calibration */}
      <article className="panel" style={{ marginBottom: 20, padding: "16px 20px" }}>
        <div className="section-header" style={{ marginBottom: 12 }}>
          <span className="badge badge-cyan">Confidence Calibration</span>
          <span className="section-count">MAE: {(Number(calibration.mean_absolute_error || 0) * 100).toFixed(1)}%</span>
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          {(calibration.bins || []).map((row) => {
            const predictedPct = Math.max(0, Math.min(100, Number(row.predicted || 0) * 100));
            const realizedPct = Math.max(0, Math.min(100, Number(row.realized || 0) * 100));
            return (
              <div key={row.bucket} style={{ border: "1px solid var(--border)", borderRadius: 8, padding: "8px 10px", background: "var(--surface-0)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                  <span style={{ width: 70, fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-2)" }}>{row.bucket}</span>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--accent)", width: 110 }}>
                    Pred {(predictedPct).toFixed(1)}%
                  </span>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--green)", width: 110 }}>
                    Real {(realizedPct).toFixed(1)}%
                  </span>
                  <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)" }}>
                    n={row.sample_size}
                  </span>
                </div>
                <div style={{ height: 4, borderRadius: 2, background: "var(--surface-2)", position: "relative", overflow: "hidden" }}>
                  <div style={{ position: "absolute", left: 0, top: 0, height: "100%", width: `${predictedPct}%`, background: "rgba(124,143,255,0.65)" }} />
                  <div style={{ position: "absolute", left: 0, top: 0, height: "100%", width: `${realizedPct}%`, background: "rgba(26,224,112,0.72)" }} />
                </div>
              </div>
            );
          })}
        </div>
      </article>

      {/* Filters */}
      <article className="panel" style={{ marginBottom: 20, padding: "16px 20px" }}>
        <form className="filters-bar" action="/signals" method="get">
          <div className="field-group">
            <label className="field-label">Sector</label>
            <select name="sector" defaultValue={params?.sector || ""} style={{
              height: 36, padding: "0 12px", background: "var(--surface-2)", border: "1px solid var(--border)",
              borderRadius: 8, color: "var(--text)", fontSize: 14, outline: "none", minWidth: 200
            }}>
              <option value="">All Sectors</option>
              {SECTORS.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="field-group">
            <label className="field-label">Min Confidence</label>
            <input name="min_confidence" type="number" step="0.05" min="0" max="1" defaultValue={params?.min_confidence || ""} placeholder="0.75" style={{ width: 120 }} />
          </div>
          <button type="submit" className="war-btn">Filter →</button>
          {(params?.sector || params?.min_confidence) && (
            <a href="/signals" style={{ height: 36, padding: "0 14px", display: "flex", alignItems: "center", fontSize: 13, color: "var(--text-3)", textDecoration: "none", border: "1px solid var(--border)", borderRadius: 8, fontFamily: "var(--font-mono)" }}>
              Clear
            </a>
          )}
        </form>
      </article>

      {/* Signal count bar */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, paddingBottom: 12, borderBottom: "1px solid var(--border)" }}>
        <span className="live-dot" />
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          {signals.length} signals · ranked by impact × z-score
        </span>
        <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)" }}>
          Refreshes every 30m
        </span>
      </div>

      <div className="grid cols-2">
        {signals.map((s, i) => <SignalCard key={s.id} signal={s} index={i} />)}
      </div>

      {signals.length === 0 && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "var(--text-3)" }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>◎</div>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: 13 }}>No signals match your filters</p>
          <a href="/signals" style={{ display: "inline-block", marginTop: 12, fontSize: 12, color: "var(--accent)", fontFamily: "var(--font-mono)" }}>Clear filters</a>
        </div>
      )}
    </MarketNerveShell>
  );
}
