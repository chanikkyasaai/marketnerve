import { MarketNerveShell, SignalCard } from "../../components/marketnerve-shell";
import { getSignalsData } from "../../lib/marketnerve-api.mjs";

export default async function SignalsPage({ searchParams }) {
  const params = await searchParams;
  const signals = await getSignalsData({
    sector: params?.sector || "",
    minConfidence: params?.min_confidence || "",
  });

  return (
    <MarketNerveShell
      eyebrow="Signal Scout — NSE Filing Intelligence"
      title={`SIGNAL <span class="accent">RADAR</span>`}
      subtitle="Source-cited · Z-scored · Back-tested · Audit-trailed"
    >
      <article className="panel" style={{ marginBottom: 20 }}>
        <form className="filters-bar" action="/signals" method="get">
          <div className="field-group">
            <label className="field-label">Sector Filter</label>
            <input name="sector" defaultValue={params?.sector || ""} placeholder="Information Technology" />
          </div>
          <div className="field-group">
            <label className="field-label">Min Confidence</label>
            <input name="min_confidence" type="number" step="0.01" min="0" max="1" defaultValue={params?.min_confidence || ""} placeholder="0.75" />
          </div>
          <button type="submit" className="war-btn">Apply →</button>
        </form>
      </article>

      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
        <span className="live-dot" />
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.65rem", color: "var(--text3)", letterSpacing: "0.1em" }}>
          {signals.length} SIGNALS ACTIVE — RANKED BY IMPACT SCORE
        </span>
      </div>

      <div className="grid cols-2">
        {signals.map((s, i) => <SignalCard key={s.id} signal={s} index={i} />)}
      </div>
    </MarketNerveShell>
  );
}
