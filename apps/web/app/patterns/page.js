import { MarketNerveShell, PatternCard } from "../../components/marketnerve-shell";
import { getPatternsData } from "../../lib/marketnerve-api.mjs";

export default async function PatternsPage({ searchParams }) {
  const params = await searchParams;
  const patterns = await getPatternsData({
    patternType: params?.pattern_type || "",
    ticker: params?.ticker || "",
  });

  return (
    <MarketNerveShell
      eyebrow="Pattern Mind — Technical Intelligence"
      title={`PATTERN <span class="accent2">HUB</span>`}
      subtitle="Back-tested chart patterns with win rates, R/R ratios, and failure context"
    >
      <article className="panel" style={{ marginBottom: 20 }}>
        <form className="filters-bar" action="/patterns" method="get">
          <div className="field-group">
            <label className="field-label">Pattern Type</label>
            <input name="pattern_type" defaultValue={params?.pattern_type || ""} placeholder="Golden Cross" />
          </div>
          <div className="field-group">
            <label className="field-label">Ticker Symbol</label>
            <input name="ticker" defaultValue={params?.ticker || ""} placeholder="HDFCBANK" />
          </div>
          <button type="submit" className="war-btn cyan">Scan →</button>
        </form>
      </article>

      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
        <span style={{ color: "var(--neon2)" }}>◆</span>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.65rem", color: "var(--text3)", letterSpacing: "0.1em" }}>
          {patterns.length} PATTERNS DETECTED — RANKED BY CONFIDENCE
        </span>
      </div>

      <div className="grid cols-2">
        {patterns.map((p, i) => <PatternCard key={`${p.ticker}-${p.pattern_type}`} pattern={p} index={i} />)}
      </div>
    </MarketNerveShell>
  );
}
