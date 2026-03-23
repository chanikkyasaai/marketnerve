"use client";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

const NAV = [
  ["HOME", "/"],
  ["SIGNALS", "/signals"],
  ["PATTERNS", "/patterns"],
  ["PORTFOLIO", "/portfolio"],
  ["STORY", "/story"],
  ["IPO", "/ipo"],
];

export function MarketNerveShell({ title, eyebrow, subtitle, children }) {
  return (
    <div className="page-shell">
      <header className="topbar">
        <div className="wordmark">
          <div className="wordmark-icon">MN</div>
          <div className="wordmark-text">
            <span className="wordmark-name">MARKET<span>NERVE</span></span>
            <span className="wordmark-tagline">Indian Equities War Room</span>
          </div>
        </div>

        <div className="topbar-center">
          <div className="live-indicator">
            <span className="live-dot" />
            <span className="live-label">Live Feed</span>
          </div>
        </div>

        <nav className="nav">
          {NAV.map(([label, href]) => (
            <Link key={href} href={href} className="nav-link">{label}</Link>
          ))}
        </nav>
      </header>

      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        {title && <h1 className="page-title" dangerouslySetInnerHTML={{ __html: title }} />}
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </motion.div>

      {children}
    </div>
  );
}

export function StatBar({ stats }) {
  return (
    <div className="stat-bar">
      {stats.map((s, i) => (
        <motion.article
          key={s.label}
          className={`stat-card ${s.accent ?? ""}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.07, duration: 0.35 }}
        >
          <div className="stat-label">{s.label}</div>
          <div className={`stat-value flicker ${s.tone ?? ""}`}>{s.value}</div>
          {s.sub && <div className="stat-sub">{s.sub}</div>}
        </motion.article>
      ))}
    </div>
  );
}

export function SignalCard({ signal, index = 0 }) {
  const conf = Math.round((signal.confidence ?? 0) * 100);
  const zScore = signal.z_score ?? signal.anomaly_score ?? 0;
  const zPct = Math.min(100, (zScore / 4) * 100);
  const winRate = Math.round((signal.backtest?.win_rate ?? signal.historical_win_rate ?? 0) * 100);
  const avgRet = ((signal.backtest?.avg_30d_return ?? signal.avg_30d_return ?? 0) * 100).toFixed(1);
  const isPos = parseFloat(avgRet) >= 0;
  const sources = signal.sources ?? [];

  return (
    <motion.article
      className="panel interactive corner-ornament"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4 }}
      whileHover={{ scale: 1.01 }}
    >
      <div className="signal-card-header">
        <div>
          <span className="badge badge-neon">{signal.signal_type}</span>
          <div className="signal-company">{signal.company}</div>
          <span className="signal-ticker-badge">{signal.ticker}</span>
        </div>
        <div className="confidence-readout">
          <div className="confidence-number">{conf}%</div>
          <div className="confidence-label">Confidence</div>
        </div>
      </div>

      <p className="signal-headline">{signal.headline}</p>
      <p className="signal-summary">{signal.summary}</p>

      <div className="anomaly-bar-wrap">
        <div className="anomaly-bar-header">
          <span className="anomaly-bar-label">Anomaly Z-Score</span>
          <span className="anomaly-bar-value">{zScore.toFixed(1)}σ</span>
        </div>
        <div className="anomaly-track">
          <motion.div
            className="anomaly-fill"
            initial={{ width: 0 }}
            animate={{ width: `${zPct}%` }}
            transition={{ delay: 0.3 + index * 0.08, duration: 0.7, ease: "easeOut" }}
          />
        </div>
      </div>

      <div className="meta-row">
        <div>
          <div className="meta-cell-key">Win Rate</div>
          <div className="meta-cell-val pos">{winRate}%</div>
        </div>
        <div>
          <div className="meta-cell-key">Avg 30D</div>
          <div className={`meta-cell-val ${isPos ? "pos" : "neg"}`}>{isPos ? "+" : ""}{avgRet}%</div>
        </div>
        <div>
          <div className="meta-cell-key">Portfolio Δ</div>
          <div className="meta-cell-val warn">{(signal.portfolio_impact_pct ?? 0).toFixed(1)}%</div>
        </div>
        <div>
          <div className="meta-cell-key">Age</div>
          <div className="meta-cell-val">{signal.age_minutes ?? 0}m</div>
        </div>
      </div>

      <div className="source-pills">
        {sources.map((src) => (
          <span key={typeof src === "string" ? src : src.name} className="source-pill">
            {typeof src === "string" ? src : src.name}
          </span>
        ))}
      </div>

      <Link href={`/audit/${signal.id}`} className="audit-btn">
        ↗ Audit Trail
      </Link>
    </motion.article>
  );
}

export function PatternCard({ pattern, index = 0 }) {
  const wins = pattern.backtest?.wins ?? pattern.wins ?? 0;
  const occ = pattern.backtest?.occurrences ?? pattern.occurrences ?? 1;
  const winPct = Math.round((wins / occ) * 100);
  const rr = pattern.backtest?.reward_risk_ratio?.toFixed(1) ?? "—";
  const strengthMap = {
    "High conviction": "badge-neon",
    "Actionable": "badge-cyan",
    "Emerging": "badge-amber",
  };
  const badgeClass = strengthMap[pattern.signal_strength] ?? "badge-amber";

  return (
    <motion.article
      className="panel interactive cyan"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4 }}
      whileHover={{ scale: 1.01 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10, marginBottom: 10 }}>
        <div>
          <span className={`badge ${badgeClass}`}>{pattern.signal_strength ?? pattern.pattern_type}</span>
          <div style={{ fontFamily: "var(--font-display)", fontSize: "1.25rem", letterSpacing: "0.06em", margin: "6px 0 3px", color: "var(--text)" }}>
            {pattern.company}
          </div>
          <span className="signal-ticker-badge" style={{ borderColor: "var(--border3)", color: "var(--neon2)", background: "var(--neon2-dim)" }}>
            {pattern.ticker}
          </span>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{ fontFamily: "var(--font-display)", fontSize: "2.2rem", color: "var(--neon2)", textShadow: "0 0 20px rgba(0,229,255,0.4)", lineHeight: 1 }}>
            {Math.round(pattern.confidence * 100)}%
          </div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.58rem", color: "var(--text3)", letterSpacing: "0.12em", textTransform: "uppercase" }}>
            {pattern.pattern_type}
          </div>
        </div>
      </div>

      <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", lineHeight: 1.65, color: "var(--text2)", marginBottom: 12 }}>
        {pattern.narrative}
      </p>

      <div className="win-bar-wrap">
        <div className="anomaly-bar-header">
          <span className="anomaly-bar-label">Win Rate · {wins}/{occ}</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--neon2)", fontWeight: 600 }}>{winPct}%</span>
        </div>
        <div className="win-bar-track">
          <motion.div
            className="win-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: `${winPct}%` }}
            transition={{ delay: 0.3 + index * 0.08, duration: 0.7, ease: "easeOut" }}
          />
        </div>
      </div>

      <div className="meta-row" style={{ marginTop: 8 }}>
        <div>
          <div className="meta-cell-key">R/R Ratio</div>
          <div className="meta-cell-val warn rr-badge">{rr}</div>
        </div>
        <div>
          <div className="meta-cell-key">30D Return</div>
          <div className="meta-cell-val pos">{((pattern.backtest?.avg_30d_return ?? pattern.avg_30d_return ?? 0) * 100).toFixed(1)}%</div>
        </div>
        <div>
          <div className="meta-cell-key">Cap Band</div>
          <div className="meta-cell-val">{pattern.market_cap_band ?? "—"}</div>
        </div>
        <div>
          <div className="meta-cell-key">Sector</div>
          <div className="meta-cell-val">{(pattern.sector ?? "—").split(" ")[0]}</div>
        </div>
      </div>

      {(pattern.risk_flags ?? []).length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 8 }}>
          {pattern.risk_flags.map((f) => (
            <span key={f} className="badge badge-red" style={{ fontSize: "0.58rem" }}>⚠ {f.slice(0, 30)}{f.length > 30 ? "…" : ""}</span>
          ))}
        </div>
      )}
    </motion.article>
  );
}

export function StoryArcCard({ arc, index = 0 }) {
  const sentColors = {
    bullish: "badge-neon",
    constructive: "badge-cyan",
    "cautiously-positive": "badge-amber",
    "high-activity": "badge-orange",
    neutral: "badge-purple",
    bearish: "badge-red",
  };

  return (
    <motion.article
      className="panel"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span className="badge badge-purple">Story Arc</span>
        <div style={{ display: "flex", gap: 8 }}>
          <span className={`badge ${sentColors[arc.sentiment] ?? "badge-amber"}`}>{arc.sentiment}</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--neon)", fontWeight: 600 }}>
            {Math.round((arc.sentiment_score ?? 0.5) * 100)}%
          </span>
        </div>
      </div>

      <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.2rem", letterSpacing: "0.05em", color: "var(--text)", marginBottom: 6 }}>
        {arc.title}
      </h3>
      <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.74rem", lineHeight: 1.6, color: "var(--text2)", marginBottom: 14 }}>
        {arc.thesis}
      </p>

      <div>
        {(arc.events ?? []).map((e, i) => (
          <div key={`${e.date}-${i}`} className="timeline-event">
            <div className="timeline-ts">{e.date}</div>
            <div className="timeline-content">
              <div className="timeline-label">{e.label}</div>
              <div className="timeline-source">{e.source}</div>
            </div>
          </div>
        ))}
      </div>

      {(arc.what_to_watch_next ?? []).length > 0 && (
        <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid var(--border)" }}>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.58rem", letterSpacing: "0.16em", textTransform: "uppercase", color: "var(--text3)", marginBottom: 8 }}>
            Watch Next
          </p>
          {arc.what_to_watch_next.map((item) => (
            <p key={item} style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--text2)", marginBottom: 4 }}>
              <span style={{ color: "var(--neon)", marginRight: 8 }}>→</span>{item}
            </p>
          ))}
        </div>
      )}
    </motion.article>
  );
}

export function IpoCard({ ipo, index = 0 }) {
  const riskBadge = ipo.risk_level === "Aggressive" ? "badge-red" : ipo.risk_level === "Balanced" ? "badge-amber" : "badge-neon";
  const subPct = Math.min(100, (ipo.subscription_multiple / 15) * 100);
  const allotPct = Math.round(ipo.allotment_probability * 100);

  return (
    <motion.article
      className="panel interactive amber-panel corner-ornament"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.09, duration: 0.4 }}
      whileHover={{ scale: 1.01 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 12 }}>
        <div>
          <div style={{ fontFamily: "var(--font-display)", fontSize: "1.2rem", letterSpacing: "0.05em", color: "var(--text)", marginBottom: 6 }}>
            {ipo.name}
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <span className={`badge ${riskBadge}`}>{ipo.risk_level}</span>
            <span className="badge badge-amber">{ipo.demand_label}</span>
          </div>
        </div>
        <div className="gmp-readout">
          <div className="gmp-val">+₹{ipo.gmp}</div>
          <div className="gmp-label">GMP</div>
        </div>
      </div>

      <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.74rem", lineHeight: 1.6, color: "var(--text2)", marginBottom: 12 }}>
        {ipo.summary}
      </p>

      <div className="sub-bar-wrap">
        <div className="anomaly-bar-header">
          <span className="anomaly-bar-label">Subscription</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--amber)", fontWeight: 600 }}>
            {ipo.subscription_multiple}×
          </span>
        </div>
        <div className="sub-bar-track">
          <motion.div
            className="sub-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: `${subPct}%` }}
            transition={{ delay: 0.3 + index * 0.09, duration: 0.7, ease: "easeOut" }}
          />
        </div>
      </div>

      <div className="meta-row" style={{ marginTop: 8 }}>
        <div>
          <div className="meta-cell-key">Allot %</div>
          <div className="meta-cell-val pos">{allotPct}%</div>
        </div>
        <div>
          <div className="meta-cell-key">Price</div>
          <div className="meta-cell-val amber">{ipo.cutoff_price ? `₹${ipo.cutoff_price}` : "—"}</div>
        </div>
        <div>
          <div className="meta-cell-key">Listing</div>
          <div className="meta-cell-val">{ipo.listing_date ?? "—"}</div>
        </div>
        <div>
          <div className="meta-cell-key">Sub×</div>
          <div className="meta-cell-val amber">{ipo.subscription_multiple}</div>
        </div>
      </div>
    </motion.article>
  );
}
