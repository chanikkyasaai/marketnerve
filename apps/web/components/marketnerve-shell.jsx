"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  ["Home", "/"],
  ["Signals", "/signals"],
  ["Patterns", "/patterns"],
  ["Portfolio", "/portfolio"],
  ["Story", "/story"],
  ["IPO", "/ipo"],
];

export function MarketNerveShell({ title, eyebrow, subtitle, children }) {
  return (
    <div className="page-shell">
      <header className="topbar">
        <div className="wordmark">
          <span className="wordmark-dot" />
          <span className="wordmark-name">Market<span>Nerve</span></span>
        </div>
        <nav className="nav">
          {navItems.map(([label, href]) => (
            <Link key={href} href={href}>{label}</Link>
          ))}
        </nav>
      </header>

      <div className="page-header">
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        {title && <h1 className="page-title">{title}</h1>}
        {subtitle && <p className="page-subtitle subtle">{subtitle}</p>}
      </div>

      {children}
    </div>
  );
}

export function MetricCard({ label, value, tone = "default", subtext }) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <span className="metric-card__label">{label}</span>
      <strong className="metric-card__value">{value}</strong>
      {subtext && <span className="small subtle">{subtext}</span>}
    </article>
  );
}

export function SignalCard({ signal }) {
  const zPct = Math.min(100, ((signal.z_score ?? signal.anomaly_score ?? 0) / 4) * 100);
  const winPct = Math.round((signal.backtest?.win_rate ?? signal.historical_win_rate ?? 0) * 100);
  const isPositive = (signal.backtest?.avg_30d_return ?? signal.avg_30d_return ?? 0) >= 0;

  return (
    <article className="panel interactive">
      <div className="signal-card__header">
        <div>
          <span className="chip chip-green">{signal.signal_type}</span>
          <p className="signal-card__company">{signal.company}</p>
          <span className="ticker">{signal.ticker}</span>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="confidence-score">{Math.round(signal.confidence * 100)}%</div>
          <div className="score-label">confidence</div>
        </div>
      </div>

      <p className="signal-headline">{signal.headline}</p>
      <p className="signal-summary">{signal.summary}</p>

      {/* Z-Score bar */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
          <span className="small mono text-faint">Anomaly Score</span>
          <span className="small mono text-green">{(signal.z_score ?? signal.anomaly_score ?? 0).toFixed(1)}σ</span>
        </div>
        <div className="z-score-bar">
          <div className="z-score-bar__fill" style={{ width: `${zPct}%` }} />
        </div>
      </div>

      <div className="meta-grid">
        <div className="meta-item">
          <span className="meta-item__key">Win Rate</span>
          <span className="meta-item__val">{winPct}%</span>
        </div>
        <div className="meta-item">
          <span className="meta-item__key">Avg 30D</span>
          <span className={`meta-item__val ${isPositive ? "positive" : "negative"}`}>
            {isPositive ? "+" : ""}{(((signal.backtest?.avg_30d_return ?? signal.avg_30d_return) ?? 0) * 100).toFixed(1)}%
          </span>
        </div>
        <div className="meta-item">
          <span className="meta-item__key">Portfolio Δ</span>
          <span className="meta-item__val">{(signal.portfolio_impact_pct ?? 0).toFixed(1)}%</span>
        </div>
        <div className="meta-item">
          <span className="meta-item__key">Age</span>
          <span className="meta-item__val">{signal.age_minutes ?? 0}m</span>
        </div>
      </div>

      <div className="tags">
        {(signal.sources ?? []).map((src) => (
          <span key={typeof src === "string" ? src : src.name} className="source-tag">
            {typeof src === "string" ? src : src.name}
          </span>
        ))}
      </div>

      <Link href={`/audit/${signal.id}`} className="audit-link">
        ↗ Open audit trail
      </Link>
    </article>
  );
}

export function PatternCard({ pattern }) {
  const winPct = Math.round((pattern.backtest?.win_rate ?? (pattern.wins / pattern.occurrences)) * 100);
  const strengthColor = pattern.signal_strength === "High conviction" ? "chip-green" : pattern.signal_strength === "Actionable" ? "chip-amber" : "chip-blue";

  return (
    <article className="panel interactive">
      <div className="card-row" style={{ marginBottom: 12 }}>
        <div>
          <span className={`chip ${strengthColor}`}>{pattern.signal_strength ?? pattern.pattern_type}</span>
          <p style={{ fontWeight: 600, marginTop: 8, fontSize: "1rem" }}>{pattern.company}</p>
          <span className="ticker">{pattern.ticker}</span>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="confidence-score" style={{ fontSize: "1.6rem" }}>{Math.round(pattern.confidence * 100)}%</div>
          <div className="score-label">{pattern.pattern_type}</div>
        </div>
      </div>

      <p className="signal-summary">{pattern.narrative}</p>

      {/* Win-rate progress bar */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
          <span className="small mono text-faint">Win rate</span>
          <span className="small mono text-green">{pattern.backtest?.wins ?? pattern.wins}/{pattern.backtest?.occurrences ?? pattern.occurrences}</span>
        </div>
        <div className="progress-bar">
          <div className="progress-bar__fill green" style={{ width: `${winPct}%` }} />
        </div>
      </div>

      <p className="subtle small">{pattern.context}</p>

      {(pattern.risk_flags ?? []).length > 0 && (
        <div className="tags" style={{ marginTop: 12 }}>
          {pattern.risk_flags.map((f) => (
            <span key={f} className="chip chip-amber" style={{ fontSize: "0.68rem" }}>⚠ {f}</span>
          ))}
        </div>
      )}
    </article>
  );
}

export function StoryArcCard({ arc }) {
  const sentimentColor = arc.sentiment === "bullish" ? "chip-green"
    : arc.sentiment === "constructive" ? "chip-blue"
    : arc.sentiment === "neutral" ? "chip-purple"
    : "chip-amber";

  return (
    <article className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <span className="chip chip-purple">Story Arc</span>
        <span className={`chip ${sentimentColor}`}>{arc.sentiment}</span>
      </div>
      <h3 style={{ marginBottom: 8, fontSize: "1.05rem" }}>{arc.title}</h3>
      <p className="subtle small">{arc.thesis}</p>
      <div className="timeline" style={{ marginTop: 16 }}>
        {arc.events.map((event) => (
          <div key={`${event.date}-${event.label}`} className="timeline-item">
            <div className="timeline-date">{event.date}</div>
            <div className="timeline-label">{event.label}</div>
            <div className="timeline-source">{event.source}</div>
          </div>
        ))}
      </div>
      {(arc.what_to_watch_next ?? []).length > 0 && (
        <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
          <p className="small mono text-faint" style={{ marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>Watch</p>
          {arc.what_to_watch_next.map((item) => (
            <p key={item} className="small subtle" style={{ marginBottom: 4 }}>→ {item}</p>
          ))}
        </div>
      )}
    </article>
  );
}

export function IpoCard({ ipo }) {
  const riskColor = ipo.risk_level === "Aggressive" ? "chip-red" : ipo.risk_level === "Balanced" ? "chip-amber" : "chip-green";
  const subPct = Math.min(100, (ipo.subscription_multiple / 15) * 100);

  return (
    <article className="panel interactive">
      <div className="card-row" style={{ marginBottom: 14 }}>
        <div>
          <h3 style={{ fontSize: "1rem", marginBottom: 6 }}>{ipo.name}</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <span className={`chip ${riskColor}`}>{ipo.risk_level}</span>
          </div>
        </div>
        <div className="gmp-badge">
          <span className="gmp-badge__value">+₹{ipo.gmp}</span>
          <span className="gmp-badge__label">GMP</span>
        </div>
      </div>

      <p className="subtle small">{ipo.summary}</p>

      <div style={{ margin: "14px 0" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
          <span className="small mono text-faint">Subscription</span>
          <span className="small mono text-amber">{ipo.subscription_multiple}×</span>
        </div>
        <div className="progress-bar">
          <div className="progress-bar__fill amber" style={{ width: `${subPct}%` }} />
        </div>
      </div>

      <div className="meta-grid">
        <div className="meta-item">
          <span className="meta-item__key">Allotment %</span>
          <span className="meta-item__val">{Math.round(ipo.allotment_probability * 100)}%</span>
        </div>
        {ipo.cutoff_price && (
          <div className="meta-item">
            <span className="meta-item__key">Price</span>
            <span className="meta-item__val">₹{ipo.cutoff_price}</span>
          </div>
        )}
        {ipo.listing_date && (
          <div className="meta-item">
            <span className="meta-item__key">Listing</span>
            <span className="meta-item__val">{ipo.listing_date}</span>
          </div>
        )}
      </div>
    </article>
  );
}
