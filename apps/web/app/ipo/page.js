import { IpoCard, MarketNerveShell } from "../../components/marketnerve-shell";
import { getIpoData, getHealthData } from "../../lib/marketnerve-api.mjs";

export default async function IpoPage() {
  let ipos = [];
  let health = { market_status: "loading" };
  try {
    [ipos, health] = await Promise.all([
      getIpoData(),
      getHealthData(),
    ]);
  } catch (e) {
    console.error("IPO page data fetch failed:", e);
  }
  
  const topIpo = ipos?.[0];
  const totalSub = ipos?.reduce((a, i) => a + (i.subscription_multiple || 0), 0) || 0;
  const avgSub = ipos?.length ? (totalSub / ipos.length).toFixed(1) : 0;
  const hotCount = ipos?.filter((i) => i.demand_label === "Hot").length || 0;

  return (
    <MarketNerveShell
      marketStatus={health.market_status}
      eyebrow="Primary Market Intelligence"
      title={`IPO <span class="accent">Command</span>`}
      subtitle="GMP tracking · Subscription multiples · Allotment probability · Listing intelligence"
    >
      {/* Quick stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { label: "Active Windows", value: ipos.length, color: "var(--text)" },
          { label: "Hot Demand", value: hotCount, color: "var(--red)" },
          { label: "Avg Subscription", value: `${avgSub}×`, color: "var(--amber)" },
          { label: "Best GMP", value: `+₹${Math.max(...ipos.map((i) => i.gmp ?? 0))}`, color: "var(--green)" },
        ].map((s) => (
          <div key={s.label} className="panel" style={{ padding: "14px 18px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</span>
            <span style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: "18px", color: s.color, letterSpacing: "-0.02em" }}>{s.value}</span>
          </div>
        ))}
      </div>

      {/* Hero IPO */}
      {topIpo && (
        <article className="panel hot" style={{ marginBottom: 24, padding: 24 }}>
          <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 16 }}>
            <span className="live-dot" />
            <span className="badge badge-amber">Hottest Window</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", marginLeft: "auto" }}>
              {topIpo.demand_label} · {topIpo.risk_level} Risk
            </span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 24 }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "var(--font-ui)", fontWeight: 800, fontSize: "24px", color: "var(--text)", marginBottom: 8, letterSpacing: "-0.02em" }}>
                {topIpo.name}
              </div>
              <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.7, color: "var(--text-2)", marginBottom: 20 }}>
                {topIpo.summary}
              </p>
              <div style={{ display: "flex", gap: 32 }}>
                {[
                  ["Subscription", `${topIpo.subscription_multiple}×`, "var(--amber)"],
                  ["Allotment", `${Math.round(topIpo.allotment_probability * 100)}%`, "var(--green)"],
                  ["Price", topIpo.cutoff_price ? `₹${topIpo.cutoff_price}` : "—", "var(--text)"],
                  ["Listing", topIpo.listing_date ?? "—", "var(--cyan)"],
                ].map(([k, v, color]) => (
                  <div key={k}>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: 4 }}>{k}</div>
                    <div style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: "18px", color, letterSpacing: "-0.02em" }}>{v}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="gmp-readout" style={{ alignSelf: "flex-start" }}>
              <div className="gmp-val" style={{ fontSize: "28px" }}>+₹{topIpo.gmp}</div>
              <div className="gmp-label">Grey Market Premium</div>
            </div>
          </div>
        </article>
      )}

      <div style={{ marginBottom: 16, paddingBottom: 12, borderBottom: "1px solid var(--border)", display: "flex", gap: 10, alignItems: "center" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
          All Active IPOs · sorted by subscription
        </span>
      </div>

      <div className="grid cols-2">
        {ipos.map((ipo, i) => <IpoCard key={ipo.name} ipo={ipo} index={i} />)}
      </div>
    </MarketNerveShell>
  );
}
