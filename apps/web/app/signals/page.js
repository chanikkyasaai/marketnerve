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
      eyebrow="Signal Scout"
      title="Live Signal Radar"
      subtitle="Ranked market signals with source-cited context, Z-score anomaly scoring, and full audit trails."
    >
      <section className="panel" style={{ marginBottom: 20 }}>
        <form className="filters-grid" action="/signals" method="get">
          <label>
            Sector
            <input name="sector" defaultValue={params?.sector || ""} placeholder="Information Technology" />
          </label>
          <label>
            Min Confidence
            <input name="min_confidence" type="number" step="0.01" min="0" max="1" defaultValue={params?.min_confidence || ""} placeholder="0.75" />
          </label>
          <button type="submit">Apply filters</button>
        </form>
      </section>

      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
        <span className="status-dot live" />
        <span className="small mono text-faint">{signals.length} signals — sorted by impact score</span>
      </div>

      <section className="grid columns-2">
        {signals.map((signal) => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </section>
    </MarketNerveShell>
  );
}
