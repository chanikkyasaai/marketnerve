import { IpoCard, MarketNerveShell, MetricCard, PatternCard, SignalCard, StoryArcCard } from "../components/marketnerve-shell";
import { getHealthData, getLatestVideoData, getPatternsData, getSignalsData, getStoryArcData } from "../lib/marketnerve-api.mjs";

export default async function HomePage() {
  const [signals, patterns, health, video, leadArc] = await Promise.all([
    getSignalsData(),
    getPatternsData(),
    getHealthData(),
    getLatestVideoData(),
    getStoryArcData("zomato"),
  ]);

  const topSignal = signals[0];

  return (
    <MarketNerveShell
      eyebrow="Live Intelligence Platform"
      title="Indian Equities Intelligence"
      subtitle="Autonomous signals, chart patterns, and portfolio-aware analysis — all back-tested, all source-cited."
    >
      {/* ── Hero ── */}
      <section className="hero">
        <article className="panel hero-panel-lead">
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <span className="status-dot live" />
            <span className="chip chip-green">Priority Signal</span>
            <span className="small mono text-faint">{topSignal.age_minutes ?? 0}m ago</span>
          </div>
          <h2 style={{ fontSize: "1.4rem", marginBottom: 6 }}>{topSignal.company}</h2>
          <span className="ticker">{topSignal.ticker}</span>
          <p className="headline-text" style={{ margin: "14px 0 10px" }}>{topSignal.headline}</p>
          <p className="subtle small">{topSignal.summary}</p>
          <div className="tags" style={{ marginTop: 14 }}>
            {(topSignal.watch_items ?? []).map((item) => (
              <span key={item} className="tag">{item}</span>
            ))}
          </div>
        </article>

        <article className="panel hero-panel-secondary">
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <span className="chip chip-amber">Today's Wrap</span>
          </div>
          <h2 style={{ fontSize: "1.15rem", marginBottom: 10 }}>{video.title}</h2>
          <p className="subtle small">{video.summary}</p>
          <div className="meta-grid" style={{ marginTop: 16 }}>
            <div className="meta-item">
              <span className="meta-item__key">Duration</span>
              <span className="meta-item__val">{video.duration_seconds}s</span>
            </div>
            <div className="meta-item">
              <span className="meta-item__key">Format</span>
              <span className="meta-item__val">Reel + Wide</span>
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            {(video.script_outline ?? []).slice(0, 3).map((step, i) => (
              <p key={i} className="small subtle" style={{ marginBottom: 5 }}>
                <span className="mono text-amber" style={{ marginRight: 6 }}>{i + 1}.</span>{step}
              </p>
            ))}
          </div>
        </article>
      </section>

      {/* ── Metrics ── */}
      <section className="metric-row">
        <MetricCard label="Live Signals" value={String(signals.length)} tone="positive" subtext="Ranked by impact" />
        <MetricCard label="Patterns Detected" value={String(patterns.length)} tone="warning" subtext="NSE universe scan" />
        <MetricCard label="Data Freshness" value={`${health.data_freshness_minutes}m`} subtext="Last ingestion" />
        <MetricCard label="API P95" value={`${health.api_p95_ms}ms`} subtext="Response latency" />
      </section>

      {/* ── Signal + Pattern Grid ── */}
      <section className="grid columns-2">
        <div className="grid">
          <h2 style={{ fontSize: "1.05rem", paddingBottom: 4, borderBottom: "1px solid var(--border)", marginBottom: 4 }}>
            <span className="text-green">●</span> Signal Radar
          </h2>
          {signals.slice(0, 3).map((signal) => (
            <SignalCard key={signal.id} signal={signal} />
          ))}
        </div>
        <div className="grid">
          <h2 style={{ fontSize: "1.05rem", paddingBottom: 4, borderBottom: "1px solid var(--border)", marginBottom: 4 }}>
            <span className="text-amber">◆</span> Pattern Hub
          </h2>
          {patterns.slice(0, 2).map((pattern) => (
            <PatternCard key={`${pattern.ticker}-${pattern.pattern_type}`} pattern={pattern} />
          ))}
          <StoryArcCard arc={leadArc} />
        </div>
      </section>
    </MarketNerveShell>
  );
}
