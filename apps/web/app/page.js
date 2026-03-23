import { IpoCard, MarketNerveShell, PatternCard, SignalCard, StatBar, StoryArcCard } from "../components/marketnerve-shell";
import { getHealthData, getIpoData, getLatestVideoData, getPatternsData, getSignalsData, getStoryArcData } from "../lib/marketnerve-api.mjs";

export default async function HomePage() {
  const [signals, patterns, health, video, arcs] = await Promise.all([
    getSignalsData(),
    getPatternsData(),
    getHealthData(),
    getLatestVideoData(),
    Promise.all(["zomato", "hdfc", "nifty-it"].map((q) => getStoryArcData(q))),
  ]);
  const ipos = await getIpoData();
  const topSignal = signals[0];

  return (
    <MarketNerveShell
      eyebrow="NSE Intelligence Platform"
      title={`INDIA<span class="accent"> MARKET</span><br/>WAR ROOM`}
      subtitle="Autonomous signals · Back-tested patterns · Portfolio X-Ray · AI-generated stories"
    >
      {/* ── STAT BAR ── */}
      <StatBar stats={[
        { label: "Active Signals", value: String(signals.length), accent: "", sub: "Ranked by impact · Z-scored" },
        { label: "Data Freshness", value: `${health.data_freshness_minutes}m`, accent: "cyan-accent", tone: "cyan", sub: "Last ingestion cycle" },
        { label: "Signals Processed", value: (health.total_signals_processed ?? 0).toLocaleString("en-IN"), accent: "amber-accent", tone: "amber", sub: "All-time pipeline count" },
        { label: "API P95 Latency", value: `${health.api_p95_ms}ms`, accent: "", tone: "white", sub: "Response time" },
      ]} />

      {/* ── HERO 2-PANEL ── */}
      <div className="hero anim-fade-up">
        {/* Lead signal */}
        <article className="panel hot corner-ornament">
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
            <span className="live-dot" />
            <span className="badge badge-neon">Priority Signal</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--text3)", marginLeft: "auto" }}>
              {topSignal.age_minutes ?? 0}m ago
            </span>
          </div>
          <div style={{ fontFamily: "var(--font-display)", fontSize: "2rem", letterSpacing: "0.05em", color: "var(--text)", marginBottom: 6 }}>
            {topSignal.company}
          </div>
          <span className="signal-ticker-badge" style={{ marginBottom: 14, display: "inline-block" }}>{topSignal.ticker}</span>
          <p style={{ fontSize: "1rem", fontWeight: 500, lineHeight: 1.5, color: "var(--text)", marginBottom: 10 }}>
            {topSignal.headline}
          </p>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.76rem", lineHeight: 1.65, color: "var(--text2)", marginBottom: 16 }}>
            {topSignal.summary}
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {(topSignal.watch_items ?? []).map((item) => (
              <span key={item} style={{ padding: "3px 10px", borderRadius: 2, fontFamily: "var(--font-mono)", fontSize: "0.62rem", border: "1px solid var(--border)", color: "var(--text2)" }}>
                {item}
              </span>
            ))}
          </div>
        </article>

        {/* Video wrap */}
        <article className="panel amber-panel corner-ornament">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <span className="badge badge-amber">📹 Daily Wrap</span>
          </div>
          <div style={{ fontFamily: "var(--font-display)", fontSize: "1.4rem", letterSpacing: "0.04em", color: "var(--text)", marginBottom: 10 }}>
            {video.title}
          </div>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.74rem", lineHeight: 1.6, color: "var(--text2)", marginBottom: 14 }}>
            {video.summary}
          </p>
          <div style={{ display: "grid", gap: 6 }}>
            {(video.script_outline ?? []).map((step, i) => (
              <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--amber)", flexShrink: 0, marginTop: 1 }}>{i + 1}.</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.74rem", color: "var(--text2)", lineHeight: 1.5 }}>{step}</span>
              </div>
            ))}
          </div>
        </article>
      </div>

      {/* ── SIGNAL + PATTERN GRID ── */}
      <div className="grid cols-2 anim-fade-up-1" style={{ marginBottom: 20 }}>
        <div>
          <div className="section-header">
            <span className="live-dot" />
            <span className="section-title">Signal <span style={{ color: "var(--neon)" }}>Radar</span></span>
            <span className="section-count">{signals.length} active</span>
          </div>
          <div className="grid">
            {signals.slice(0, 3).map((s, i) => <SignalCard key={s.id} signal={s} index={i} />)}
          </div>
        </div>
        <div>
          <div className="section-header">
            <span style={{ color: "var(--neon2)" }}>◆</span>
            <span className="section-title">Pattern <span style={{ color: "var(--neon2)" }}>Hub</span></span>
            <span className="section-count">{patterns.length} detected</span>
          </div>
          <div className="grid">
            {patterns.slice(0, 3).map((p, i) => <PatternCard key={`${p.ticker}-${p.pattern_type}`} pattern={p} index={i} />)}
          </div>
        </div>
      </div>

      {/* ── STORY ARCS ── */}
      <div className="anim-fade-up-2">
        <div className="section-header" style={{ marginTop: 8 }}>
          <span style={{ color: "var(--purple)" }}>▲</span>
          <span className="section-title">Story <span style={{ color: "var(--purple)" }}>Arcs</span></span>
          <span className="section-count">3 of 5 shown</span>
        </div>
        <div className="grid cols-3">
          {arcs.map((arc, i) => <StoryArcCard key={arc.slug} arc={arc} index={i} />)}
        </div>
      </div>

      {/* ── IPO ROW ── */}
      <div className="anim-fade-up-3" style={{ marginTop: 20 }}>
        <div className="section-header">
          <span style={{ color: "var(--amber)" }}>★</span>
          <span className="section-title">IPO <span style={{ color: "var(--amber)" }}>Intelligence</span></span>
          <span className="section-count">{ipos.length} active windows</span>
        </div>
        <div className="grid cols-2">
          {ipos.slice(0, 2).map((ipo, i) => <IpoCard key={ipo.name} ipo={ipo} index={i} />)}
        </div>
      </div>
    </MarketNerveShell>
  );
}
