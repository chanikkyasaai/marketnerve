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
      eyebrow="Pattern Mind"
      title="Chart Pattern Hub"
      subtitle="Back-tested technical patterns with win rates, narratives, and risk flags — across the NSE universe."
    >
      <section className="panel" style={{ marginBottom: 20 }}>
        <form className="filters-grid" action="/patterns" method="get">
          <label>
            Pattern Type
            <input name="pattern_type" defaultValue={params?.pattern_type || ""} placeholder="Golden Cross" />
          </label>
          <label>
            Ticker Symbol
            <input name="ticker" defaultValue={params?.ticker || ""} placeholder="HDFCBANK" />
          </label>
          <button type="submit">Scan patterns</button>
        </form>
      </section>

      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
        <span className="chip chip-amber">◆</span>
        <span className="small mono text-faint">{patterns.length} patterns — ranked by confidence</span>
      </div>

      <section className="grid columns-2">
        {patterns.map((pattern) => (
          <PatternCard key={`${pattern.ticker}-${pattern.pattern_type}`} pattern={pattern} />
        ))}
      </section>
    </MarketNerveShell>
  );
}
