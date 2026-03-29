"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

const NAV = [
  { label: "Overview",    href: "/" },
  { label: "Signals",     href: "/signals" },
  { label: "Patterns",    href: "/patterns" },
  { label: "Portfolio",   href: "/portfolio" },
  { label: "Market Chat", href: "/chat" },
  { label: "Story",       href: "/story" },
  { label: "IPO",         href: "/ipo" },
];

// ── Spring animation variants ──────────────────────────────────
const containerVariants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.07, delayChildren: 0.04 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 18, scale: 0.97 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: "spring", stiffness: 280, damping: 24 },
  },
};

const cardHover = {
  y: -4,
  transition: { type: "spring", stiffness: 420, damping: 22 },
};

const pageHeaderVariants = {
  hidden: { opacity: 0, y: 14 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 300, damping: 28, delayChildren: 0.08, staggerChildren: 0.06 },
  },
};

const pageHeaderChild = {
  hidden: { opacity: 0, y: 10 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 320, damping: 26 },
  },
};

// ── Sparkline SVG ──────────────────────────────────────────────
export function Sparkline({ data, height = 36, width = 80 }) {
  if (!data || data.length < 2) return <div style={{ width, height }} />;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  const polyPts = pts.join(" ");
  const isPos = data[data.length - 1] >= data[0];
  const color = isPos ? "var(--green)" : "var(--red)";
  const areaPath = `M${pts[0]} ${pts.slice(1).map(p => `L${p}`).join(" ")} L${width},${height} L0,${height} Z`;
  const uid = `g${isPos ? "p" : "n"}${width}`;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} fill="none" style={{ display: "block", flexShrink: 0 }}>
      <defs>
        <linearGradient id={uid} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.22" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#${uid})`} />
      <polyline points={polyPts} stroke={color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// Deterministic sparkline from ticker string
function genSparkline(ticker = "X", length = 22, bias = 0) {
  const seed = ticker.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  let price = 100;
  const out = [price];
  for (let i = 1; i < length; i++) {
    const n =
      Math.sin(i * seed * 0.07 + i * 0.4) * 2.5 +
      Math.cos(i * 0.5 + seed * 0.02) * 1.5 +
      bias * 0.3;
    price = Math.max(60, price + n);
    out.push(price);
  }
  return out;
}

// ── Animated counter for stat numbers ─────────────────────────
function useCountUp(target, duration = 900) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const num = parseFloat(String(target).replace(/[^0-9.]/g, ""));
    if (isNaN(num)) { setDisplay(target); return; }
    let start = null;
    const step = (ts) => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const current = Math.round(eased * num * 10) / 10;
      setDisplay(current);
      if (progress < 1) requestAnimationFrame(step);
      else setDisplay(num);
    };
    requestAnimationFrame(step);
  }, [target, duration]);
  return display;
}

// ── Shell ──────────────────────────────────────────────────────
export function MarketNerveShell({ title, eyebrow, subtitle, children, marketStatus }) {
  const pathname = usePathname();
  const [routeLoading, setRouteLoading] = useState(false);
  const [loadingHint, setLoadingHint] = useState("Syncing market tape");

  function onNavClick(targetHref) {
    if (!targetHref || targetHref === pathname || (targetHref !== "/" && pathname.startsWith(targetHref))) {
      return;
    }
    const hints = [
      "Syncing market tape",
      "Refreshing signal graph",
      "Replaying pattern engine",
      "Warming portfolio lens",
    ];
    setLoadingHint(hints[Math.floor(Math.random() * hints.length)]);
    setRouteLoading(true);
  }

  useEffect(() => {
    if (!routeLoading) {
      return;
    }
    const timer = setTimeout(() => setRouteLoading(false), 560);
    return () => clearTimeout(timer);
  }, [pathname, routeLoading]);

  return (
    <>
      <AnimatePresence>
        {routeLoading && (
          <motion.div
            className="route-loader"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
          >
            <motion.div
              className="route-loader-card"
              initial={{ y: 10, scale: 0.98, opacity: 0.7 }}
              animate={{ y: 0, scale: 1, opacity: 1 }}
              exit={{ y: 8, scale: 0.98, opacity: 0 }}
              transition={{ type: "spring", stiffness: 280, damping: 22 }}
            >
              <div className="route-loader-orbit">
                <span className="route-loader-dot" />
                <span className="route-loader-dot alt" />
              </div>
              <div className="route-loader-texts">
                <p className="route-loader-title">Loading MarketNerve</p>
                <p className="route-loader-subtitle">{loadingHint}</p>
              </div>
              <motion.div
                className="route-loader-bar"
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* TOP NAV */}
        <header className="topbar">
          <Link href="/" className="wordmark">
            <motion.div
          className="wordmark-icon"
          whileHover={{ scale: 1.08, rotate: 3 }}
          transition={{ type: "spring", stiffness: 400, damping: 18 }}
            >
          <img src="/images/logo.png" alt="MarketNerve" style={{ width: "100%", height: "100%" }} />
            </motion.div>
            <div className="wordmark-text">
          <span className="wordmark-name">Market<span>Nerve</span></span>
          <span className="wordmark-tagline">NSE Intelligence</span>
            </div>
          </Link>

          <nav className="nav">
            {NAV.map(({ label, href }) => {
            const isActive = pathname === href || (href !== "/" && pathname.startsWith(href));
            return (
              <motion.div key={href} whileHover={{ y: -1 }} transition={{ type: "spring", stiffness: 500, damping: 25 }}>
                <Link href={href} className={`nav-link${isActive ? " active" : ""}`} onClick={() => onNavClick(href)}>
                  {label}
                </Link>
              </motion.div>
            );
          })}
        </nav>

        <div className="topbar-right">
          <div className="live-indicator">
            <span className="live-dot" />
            <span className="live-label">Live</span>
          </div>
        </div>
      </header>

      {/* MARKET TICKER */}
      {marketStatus && (
        <div className="market-ticker">
          <div className="ticker-scroll">
            {[...Object.entries(marketStatus), ...Object.entries(marketStatus)].map(([name, data], i) => (
              <div key={`${name}-${i}`} className="ticker-item">
                <span className="ticker-name">{name.replace(".NS", "").replace("NSE:", "")}</span>
                <span className="ticker-price">
                  ₹{data.price >= 10000 ? (data.price / 1000).toFixed(1) + "k" : data.price?.toLocaleString("en-IN") ?? "—"}
                </span>
                <span className={`ticker-change ${(data.p_change ?? 0) >= 0 ? "pos" : "neg"}`}>
                  {(data.p_change ?? 0) >= 0 ? "▲" : "▼"}{Math.abs(data.p_change ?? 0).toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PAGE CONTENT */}
      <div className="page-shell">
        <motion.div
          className="page-header"
          variants={pageHeaderVariants}
          initial="hidden"
          animate="show"
        >
          {eyebrow && (
            <motion.p className="eyebrow" variants={pageHeaderChild}>{eyebrow}</motion.p>
          )}
          {title && (
            <motion.h1
              className="page-title"
              variants={pageHeaderChild}
              dangerouslySetInnerHTML={{ __html: title }}
            />
          )}
          {subtitle && (
            <motion.p className="page-subtitle" variants={pageHeaderChild}>{subtitle}</motion.p>
          )}
        </motion.div>

        {children}
      </div>
    </>
  );
}

// ── StatBar ────────────────────────────────────────────────────
export function StatBar({ stats }) {
  return (
    <motion.div
      className="stat-bar"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {stats.map((s) => (
        <motion.article
          key={s.label}
          className={`stat-card${s.accent ? ` ${s.accent}` : ""}`}
          variants={itemVariants}
          whileHover={{ y: -2, transition: { type: "spring", stiffness: 400, damping: 22 } }}
        >
          <div className="stat-label">{s.label}</div>
          <div className={`stat-value${s.tone ? ` ${s.tone}` : ""}`}>{s.value}</div>
          {s.sub && <div className="stat-sub">{s.sub}</div>}
        </motion.article>
      ))}
    </motion.div>
  );
}

// ── SignalCard ─────────────────────────────────────────────────
export function SignalCard({ signal, index = 0 }) {
  const conf    = Math.round((signal.confidence ?? 0) * 100);
  const zScore  = signal.z_score ?? signal.anomaly_score ?? 0;
  const zPct    = Math.min(100, (Math.abs(zScore) / 4) * 100);
  const winRate = Math.round((signal.backtest?.win_rate ?? signal.historical_win_rate ?? 0) * 100);
  const avgRet  = ((signal.backtest?.avg_30d_return ?? signal.avg_30d_return ?? 0) * 100).toFixed(1);
  const isPos   = parseFloat(avgRet) >= 0;
  const sources = signal.sources ?? [];
  const spark   = genSparkline(signal.ticker ?? "X", 22, zScore > 0 ? 1 : -1);

  return (
    <motion.article
      className="panel interactive"
      initial={{ opacity: 0, y: 20, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 24, delay: index * 0.07 }}
      whileHover={cardHover}
    >
      <div className="signal-card-header">
        <div style={{ flex: 1, minWidth: 0 }}>
          <span className="badge badge-neon">{signal.signal_type}</span>
          <div className="signal-company">{signal.company}</div>
          <span className="signal-ticker-badge">{signal.ticker}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
          <div className="confidence-readout">
            <div className="confidence-number">{conf}%</div>
            <div className="confidence-label">Confidence</div>
          </div>
          <Sparkline data={spark} width={74} height={30} />
        </div>
      </div>

      <p className="signal-headline">{signal.headline}</p>
      <p className="signal-summary">{signal.summary}</p>

      <div className="anomaly-bar-wrap">
        <div className="anomaly-bar-header">
          <span className="anomaly-bar-label">Anomaly Z-Score</span>
          <span className="anomaly-bar-value">{zScore.toFixed(2)}σ</span>
        </div>
        <div className="anomaly-track">
          <motion.div
            className="anomaly-fill"
            initial={{ width: 0 }}
            animate={{ width: `${zPct}%` }}
            transition={{ type: "spring", stiffness: 80, damping: 18, delay: 0.2 + index * 0.07 }}
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

      <Link href={`/audit/${signal.id}`} className="audit-btn">↗ Audit Trail</Link>
    </motion.article>
  );
}

// ── PatternCard ────────────────────────────────────────────────
export function PatternCard({ pattern, index = 0 }) {
  const wins    = pattern.backtest?.wins ?? pattern.wins ?? 0;
  const occ     = pattern.backtest?.occurrences ?? pattern.occurrences ?? 1;
  const winPct  = Math.round((wins / occ) * 100);
  const rr      = (pattern.backtest?.reward_risk_ratio ?? pattern.reward_risk_ratio ?? 2.0).toFixed(1);
  const strengthMap = {
    "High conviction": "badge-neon",
    "Actionable":      "badge-cyan",
    "Emerging":        "badge-amber",
  };
  const badgeClass = strengthMap[pattern.signal_strength] ?? "badge-amber";
  const spark = genSparkline(pattern.ticker ?? "Y", 24, 0.6);

  return (
    <motion.article
      className="panel interactive cyan"
      initial={{ opacity: 0, y: 20, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 24, delay: index * 0.07 }}
      whileHover={cardHover}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 14 }}>
        <div style={{ flex: 1 }}>
          <span className={`badge ${badgeClass}`}>{pattern.signal_strength ?? pattern.pattern_type}</span>
          <div style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: 15, color: "var(--text)", margin: "7px 0 4px", letterSpacing: "-0.022em" }}>
            {pattern.company}
          </div>
          <span className="signal-ticker-badge" style={{ borderColor: "rgba(20,216,248,0.28)", color: "var(--cyan)", background: "rgba(20,216,248,0.1)" }}>
            {pattern.ticker}
          </span>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0, display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <div>
            <div style={{ fontFamily: "var(--font-ui)", fontWeight: 800, fontSize: 26, color: "var(--cyan)", letterSpacing: "-0.04em", lineHeight: 1 }}>
              {Math.round(pattern.confidence * 100)}%
            </div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-3)", letterSpacing: "0.1em", textTransform: "uppercase", marginTop: 2 }}>
              {pattern.pattern_type}
            </div>
          </div>
          <Sparkline data={spark} width={72} height={28} />
        </div>
      </div>

      <p style={{ fontFamily: "var(--font-mono)", fontSize: 12, lineHeight: 1.78, color: "var(--text-2)", marginBottom: 14 }}>
        {pattern.narrative}
      </p>

      <div className="win-bar-wrap">
        <div className="anomaly-bar-header">
          <span className="anomaly-bar-label">Win Rate · {wins}/{occ}</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--green)", fontWeight: 700 }}>{winPct}%</span>
        </div>
        <div className="win-bar-track">
          <motion.div
            className="win-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: `${winPct}%` }}
            transition={{ type: "spring", stiffness: 80, damping: 18, delay: 0.25 + index * 0.07 }}
          />
        </div>
      </div>

      <div className="meta-row" style={{ marginTop: 10 }}>
        <div>
          <div className="meta-cell-key">R/R</div>
          <div className="meta-cell-val rr-badge">{rr}x</div>
        </div>
        <div>
          <div className="meta-cell-key">30D Ret</div>
          <div className="meta-cell-val pos">{((pattern.backtest?.avg_30d_return ?? pattern.avg_30d_return ?? 0) * 100).toFixed(1)}%</div>
        </div>
        <div>
          <div className="meta-cell-key">Cap</div>
          <div className="meta-cell-val">{(pattern.market_cap_band ?? "—").split(" ")[0]}</div>
        </div>
        <div>
          <div className="meta-cell-key">Sector</div>
          <div className="meta-cell-val">{(pattern.sector ?? "—").split(" ")[0]}</div>
        </div>
      </div>

      {(pattern.risk_flags ?? []).length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 10 }}>
          {pattern.risk_flags.map((f) => (
            <span key={f} className="badge badge-red" style={{ fontSize: 10 }}>⚠ {f.slice(0, 28)}{f.length > 28 ? "…" : ""}</span>
          ))}
        </div>
      )}
    </motion.article>
  );
}

// ── StoryArcCard ───────────────────────────────────────────────
export function StoryArcCard({ arc, index = 0 }) {
  const sentStyles = {
    bullish:               { badge: "badge-neon",   bar: "var(--green)" },
    constructive:          { badge: "badge-cyan",   bar: "var(--cyan)" },
    "cautiously-positive": { badge: "badge-amber",  bar: "var(--amber)" },
    "high-activity":       { badge: "badge-amber",  bar: "var(--amber)" },
    neutral:               { badge: "badge-purple", bar: "var(--purple)" },
    bearish:               { badge: "badge-red",    bar: "var(--red)" },
  };
  const style   = sentStyles[arc.sentiment] ?? sentStyles.neutral;
  const sentPct = Math.round((arc.sentiment_score ?? 0.5) * 100);

  return (
    <motion.article
      className="panel"
      initial={{ opacity: 0, y: 16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 24, delay: index * 0.09 }}
      whileHover={{ y: -3, transition: { type: "spring", stiffness: 420, damping: 22 } }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <span className="badge badge-purple">Story Arc</span>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className={`badge ${style.badge}`}>{arc.sentiment}</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: style.bar, fontWeight: 700 }}>{sentPct}%</span>
        </div>
      </div>

      <h3 style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: 15, color: "var(--text)", marginBottom: 8, letterSpacing: "-0.022em", lineHeight: 1.42 }}>
        {arc.title}
      </h3>

      <div style={{ height: 2, background: "rgba(255,255,255,0.05)", borderRadius: 2, marginBottom: 12, overflow: "hidden" }}>
        <motion.div
          style={{ height: "100%", background: style.bar, borderRadius: 2 }}
          initial={{ width: 0 }}
          animate={{ width: `${sentPct}%` }}
          transition={{ type: "spring", stiffness: 80, damping: 18, delay: 0.3 + index * 0.09 }}
        />
      </div>

      <p style={{ fontFamily: "var(--font-mono)", fontSize: 12, lineHeight: 1.78, color: "var(--text-2)", marginBottom: 16 }}>
        {arc.thesis}
      </p>

      <div>
        {(arc.events ?? []).slice(0, 3).map((e, i) => (
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
        <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: 10 }}>
            Watch Next
          </p>
          {arc.what_to_watch_next.slice(0, 2).map((item) => (
            <p key={item} style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-2)", marginBottom: 5, display: "flex", gap: 8 }}>
              <span style={{ color: "var(--accent)", flexShrink: 0 }}>→</span>{item}
            </p>
          ))}
        </div>
      )}
    </motion.article>
  );
}

// ── IpoCard ────────────────────────────────────────────────────
export function IpoCard({ ipo, index = 0 }) {
  const riskBadge = ipo.risk_level === "Aggressive" ? "badge-red" : ipo.risk_level === "Balanced" ? "badge-amber" : "badge-neon";
  const subPct    = Math.min(100, (ipo.subscription_multiple / 20) * 100);
  const allotPct  = Math.round(ipo.allotment_probability * 100);

  return (
    <motion.article
      className="panel interactive amber-panel"
      initial={{ opacity: 0, y: 16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 24, delay: index * 0.08 }}
      whileHover={cardHover}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 14 }}>
        <div>
          <div style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: 16, color: "var(--text)", marginBottom: 8, letterSpacing: "-0.022em" }}>
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

      <p style={{ fontFamily: "var(--font-mono)", fontSize: 12, lineHeight: 1.78, color: "var(--text-2)", marginBottom: 14 }}>
        {ipo.summary}
      </p>

      <div className="sub-bar-wrap">
        <div className="anomaly-bar-header">
          <span className="anomaly-bar-label">Subscription</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--amber)", fontWeight: 700 }}>{ipo.subscription_multiple}×</span>
        </div>
        <div className="sub-bar-track">
          <motion.div
            className="sub-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: `${subPct}%` }}
            transition={{ type: "spring", stiffness: 80, damping: 18, delay: 0.25 + index * 0.08 }}
          />
        </div>
      </div>

      <div className="meta-row" style={{ marginTop: 10 }}>
        <div>
          <div className="meta-cell-key">Allotment</div>
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
          <div className="meta-cell-key">Sub ×</div>
          <div className="meta-cell-val amber">{ipo.subscription_multiple}</div>
        </div>
      </div>
    </motion.article>
  );
}
