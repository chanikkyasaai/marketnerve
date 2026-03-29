import { IpoCard, MarketNerveShell, PatternCard, SignalCard, StatBar, StoryArcCard } from "../components/marketnerve-shell";
import { LiveStatusStrip } from "../components/live-status-strip";
import { getHealthData, getIpoData, getLatestVideoData, getPatternsData, getSignalsData, getStoryArcData } from "../lib/marketnerve-api.mjs";

export default async function HomePage() {
  const [signals, patterns, health, video, ipoData] = await Promise.all([
    getSignalsData(),
    getPatternsData(),
    getHealthData(),
    getLatestVideoData(),
    getIpoData(),
  ]);
  // Fetch all available story arcs dynamically (live data only - no hardcoded topics)
  let allArcs = [];
  try {
    const arcResponse = await fetch(`${process.env.API_BASE_URL || 'http://localhost:8000'}/api/story/arcs`);
    if (arcResponse.ok) {
      const arcData = await arcResponse.json();
      allArcs = (arcData.items || []).slice(0, 3); // Top 3 arcs
    }
  } catch (e) {
    console.warn("Failed to fetch story arcs", e);
  }
  const arcs = allArcs;
  const topSignal = signals[0] ?? {};
  const topPattern = patterns[0] ?? {};
  const hasSignals = signals.length > 0;
  const hasPatterns = patterns.length > 0;
  const hasArcs = arcs.length > 0;

  const radarLeaders = signals
    .map((s) => {
      const confidence = Number(s?.confidence ?? 0);
      const z = Math.abs(Number(s?.z_score ?? s?.anomaly_score ?? 0));
      const win = Number(s?.historical_win_rate ?? 0);
      const ret = Math.abs(Number(s?.avg_30d_return ?? 0)) * 100;
      const score = Math.round((confidence * 55) + (z * 12) + (win * 25) + (Math.min(ret, 12) * 0.7));
      return {
        id: s.id,
        ticker: s.ticker,
        company: s.company,
        signalType: s.signal_type,
        headline: s.headline,
        sources: (s.sources || []).map((src) => (typeof src === "string" ? src : src?.name || "Source")),
        watchItems: s.watch_items || [],
        score,
        confidence: Math.round(confidence * 100),
        z: z.toFixed(1),
        winRate: Math.round(win * 100),
      };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  const statsData = [
    {
      label: "Live Signals",
      value: String(signals.length),
      sub: "Ranked by Z-score × impact",
      accent: "",
    },
    {
      label: "Data Freshness",
      value: `${health.data_freshness_minutes ?? 0}m`,
      sub: "Last pipeline cycle",
      accent: "cyan-accent",
      tone: "cyan",
    },
    {
      label: "Processed",
      value: (health.total_signals_processed ?? 0).toLocaleString("en-IN"),
      sub: "Signals all-time",
      accent: "amber-accent",
      tone: "amber",
    },
    {
      label: "P95 Latency",
      value: `${health.api_p95_ms ?? 0}ms`,
      sub: "API response time",
      accent: "",
      tone: "white",
    },
  ];

  return (
    <MarketNerveShell
      marketStatus={health.market_status}
      eyebrow="Intelligence Platform · NSE/BSE"
      title={`Market <span class="accent">Intelligence</span>`}
      subtitle="Autonomous signal detection · Back-tested patterns · Portfolio X-Ray · AI narratives"
    >
      <LiveStatusStrip health={health} />

      {/* Stats row */}
      <StatBar stats={statsData} />

      {/* Opportunity Radar leaderboard */}
      <div className="anim-fade-up" style={{ marginBottom: 24 }}>
        <div className="section-header">
          <span className="live-dot" />
          <span className="section-title">Opportunity Radar</span>
          <span className="section-count">Actionable score ranking</span>
        </div>
        {radarLeaders.length > 0 ? (
          <div className="grid cols-2">
            {radarLeaders.map((r, idx) => (
              <article key={r.id || `${r.ticker}-${idx}`} className="panel" style={{ padding: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <span className="badge badge-neon">#{idx + 1}</span>
                  <span className="signal-ticker-badge">{r.ticker}</span>
                  <span style={{ marginLeft: "auto", fontFamily: "var(--font-ui)", fontWeight: 800, fontSize: 20, color: "var(--green)", letterSpacing: "-0.02em" }}>
                    {r.score}
                  </span>
                </div>
                <div style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: 15, color: "var(--text)", marginBottom: 6 }}>
                  {r.company}
                </div>
                <p style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-2)", lineHeight: 1.6, marginBottom: 10 }}>
                  {r.headline}
                </p>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <span className="badge badge-cyan">{r.signalType}</span>
                  <span className="badge badge-amber">Conf {r.confidence}%</span>
                  <span className="badge badge-purple">Z {r.z}σ</span>
                  <span className="badge">Win {r.winRate}%</span>
                </div>
                <div style={{ marginTop: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {(r.sources || []).slice(0, 2).map((src) => (
                    <span key={src} style={{ padding: "3px 8px", borderRadius: 999, border: "1px solid rgba(20,216,248,0.22)", background: "rgba(20,216,248,0.08)", color: "var(--cyan)", fontFamily: "var(--font-mono)", fontSize: 10 }}>
                      {src}
                    </span>
                  ))}
                </div>
                <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {r.id ? (
                    <a href={`/audit/${r.id}`} style={{ padding: "4px 10px", borderRadius: 999, border: "1px solid rgba(124,143,255,0.3)", background: "rgba(124,143,255,0.08)", color: "var(--accent)", textDecoration: "none", fontFamily: "var(--font-mono)", fontSize: 10 }}>
                      ↗ Audit Trail
                    </a>
                  ) : null}
                  {r.watchItems?.[0] ? (
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)" }}>
                      Watch: {r.watchItems[0]}
                    </span>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <article className="panel" style={{ padding: 18 }}>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-2)" }}>
              Radar is warming up. Leaders will appear as soon as live signals are scored.
            </p>
          </article>
        )}
      </div>

      {/* Hero section: Top signal + Top pattern */}
      {hasSignals || hasPatterns ? (
      <div className="hero anim-fade-up" style={{ marginBottom: 24 }}>
        {/* Top signal hero */}
        {hasSignals && (
        <article className="panel hot" style={{ padding: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <span className="live-dot" />
            <span className="badge badge-accent">Priority Signal</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", marginLeft: "auto" }}>
              {topSignal.age_minutes ?? 0}m ago
            </span>
          </div>
          <div style={{ fontFamily: "var(--font-ui)", fontWeight: 800, fontSize: "22px", color: "var(--text)", marginBottom: 4, letterSpacing: "-0.02em", lineHeight: 1.2 }}>
            {topSignal.company}
          </div>
          <span className="signal-ticker-badge" style={{ marginBottom: 12, display: "inline-block" }}>{topSignal.ticker}</span>
          <p style={{ fontFamily: "var(--font-ui)", fontWeight: 600, fontSize: "14px", lineHeight: 1.55, color: "var(--text)", marginBottom: 10 }}>
            {topSignal.headline}
          </p>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.7, color: "var(--text-2)", marginBottom: 16 }}>
            {topSignal.summary}
          </p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)" }}>Confidence:</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--green)", fontWeight: 600 }}>
              {Math.round((topSignal.confidence ?? 0) * 100)}%
            </span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", marginLeft: 8 }}>Anomaly:</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--accent)", fontWeight: 600 }}>
              {(topSignal.z_score ?? 0).toFixed(2)}σ
            </span>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {(topSignal.watch_items ?? []).slice(0, 3).map((item) => (
              <span key={item} style={{
                padding: "4px 10px", borderRadius: 6,
                fontFamily: "var(--font-mono)", fontSize: "11px",
                border: "1px solid var(--border)", color: "var(--text-2)",
                background: "var(--surface-1)"
              }}>
                {item}
              </span>
            ))}
          </div>
        </article>
        )}

        {/* Daily intelligence wrap or loading state */}
        <article className="panel amber-panel" style={{ padding: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <span className="badge badge-amber">Market Activity</span>
          </div>
          {hasPatterns ? (
          <>
            <div style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: "17px", color: "var(--text)", marginBottom: 10, letterSpacing: "-0.01em", lineHeight: 1.3 }}>
              {topPattern.narrative || "Patterns Detected"}
            </div>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.65, color: "var(--text-2)", marginBottom: 16 }}>
              {topPattern.context || "Analyzing technical patterns across your watchlist..."}
            </p>
          </>
          ) : (
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.65, color: "var(--text-2)" }}>
            Live market analysis initializing. Signals and patterns will appear here as they're detected.
          </p>
          )}
        </article>
      </div>
      ) : (
      <div className="hero anim-fade-up" style={{ marginBottom: 24 }}>
        <article className="panel" style={{ padding: 24, textAlign: "center" }}>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "13px", color: "var(--text-2)", lineHeight: 1.6 }}>
            📡 Fetching live market signals and patterns from NSE/BSE... This usually takes 30-60 seconds on first load
          </p>
        </article>
      </div>
      )}

      {/* Signal Radar + Pattern Hub */}
      <div className="grid cols-2 anim-fade-up-1" style={{ marginBottom: 24 }}>
        <div>
          <div className="section-header">
            <span className="live-dot" />
            <span className="section-title">Signal Radar</span>
            <span className="section-count">{signals.length} active</span>
          </div>
          {hasSignals ? (
          <div className="grid">
            {signals.slice(0, 3).map((s, i) => <SignalCard key={s.id} signal={s} index={i} />)}
          </div>
          ) : (
          <div style={{ padding: "24px", textAlign: "center", color: "var(--text-2)" }}>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px" }}>Generating signals...</p>
          </div>
          )}
        </div>
        <div>
          <div className="section-header">
            <span style={{ color: "var(--cyan)", fontSize: "12px" }}>◈</span>
            <span className="section-title">Pattern Hub</span>
            <span className="section-count">{patterns.length} detected</span>
          </div>
          {hasPatterns ? (
          <div className="grid">
            {patterns.slice(0, 3).map((p, i) => <PatternCard key={`${p.ticker}-${p.pattern_type}`} pattern={p} index={i} />)}
          </div>
          ) : (
          <div style={{ padding: "24px", textAlign: "center", color: "var(--text-2)" }}>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px" }}>Analyzing patterns...</p>
          </div>
          )}
        </div>
      </div>

      {/* Story Arcs */}
      <div className="anim-fade-up-2" style={{ marginBottom: 24 }}>
        <div className="section-header">
          <span style={{ color: "var(--purple)", fontSize: "12px" }}>▲</span>
          <span className="section-title">Story Arcs</span>
          <span className="section-count">AI-generated narratives</span>
        </div>
        {hasArcs ? (
        <div className="grid cols-3">
          {arcs.map((arc, i) => <StoryArcCard key={arc.slug || arc.id} arc={arc} index={i} />)}
        </div>
        ) : (
        <div style={{ padding: "24px", textAlign: "center", backgroundColor: "var(--surface-1)", borderRadius: "12px", color: "var(--text-2)" }}>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px" }}>Fetching market narratives...</p>
        </div>
        )}
      </div>

      {/* IPO Intelligence */}
      <div className="anim-fade-up-3">
        <div className="section-header">
          <span style={{ color: "var(--amber)", fontSize: "12px" }}>★</span>
          <span className="section-title">IPO Intelligence</span>
          <span className="section-count">{ipoData.length} active windows</span>
        </div>
        <div className="grid cols-2">
          {ipoData.slice(0, 2).map((ipo, i) => <IpoCard key={ipo.name} ipo={ipo} index={i} />)}
        </div>
      </div>
    </MarketNerveShell>
  );
}
