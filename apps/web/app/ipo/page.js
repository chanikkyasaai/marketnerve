import { IpoCard, MarketNerveShell } from "../../components/marketnerve-shell";
import { getIpoData } from "../../lib/marketnerve-api.mjs";

export default async function IpoPage() {
  const ipos = await getIpoData();
  const topIpo = ipos[0];

  return (
    <MarketNerveShell
      eyebrow="Primary Market Intelligence"
      title={`IPO <span class="accent">COMMAND</span>`}
      subtitle="GMP · Subscription multiples · Allotment odds · Listing date countdown"
    >
      {/* Top IPO Hero */}
      {topIpo && (
        <article className="panel hot corner-ornament" style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 14 }}>
            <span className="live-dot" />
            <span className="badge badge-amber">🔥 Hottest Window</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--text3)", marginLeft: "auto" }}>
              {topIpo.demand_label} · {topIpo.risk_level} Risk
            </span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 20 }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "var(--font-display)", fontSize: "2rem", letterSpacing: "0.06em", color: "var(--text)", marginBottom: 8 }}>
                {topIpo.name}
              </div>
              <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.76rem", lineHeight: 1.65, color: "var(--text2)", marginBottom: 16 }}>
                {topIpo.summary}
              </p>
              <div style={{ display: "flex", gap: 24 }}>
                {[
                  ["Subscription", `${topIpo.subscription_multiple}×`, "amber"],
                  ["Allotment", `${Math.round(topIpo.allotment_probability * 100)}%`, ""],
                  ["Price", topIpo.cutoff_price ? `₹${topIpo.cutoff_price}` : "—", ""],
                  ["Listing", topIpo.listing_date ?? "—", "cyan"],
                ].map(([k, v, tone]) => (
                  <div key={k}>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.58rem", letterSpacing: "0.14em", textTransform: "uppercase", color: "var(--text3)", marginBottom: 4 }}>{k}</div>
                    <div style={{ fontFamily: "var(--font-display)", fontSize: "1.4rem", letterSpacing: "0.04em", color: tone === "amber" ? "var(--amber)" : tone === "cyan" ? "var(--neon2)" : "var(--neon)", textShadow: tone === "amber" ? "0 0 16px rgba(255,183,0,0.4)" : "0 0 16px rgba(0,255,136,0.4)" }}>
                      {v}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="gmp-readout" style={{ alignSelf: "flex-start" }}>
              <div className="gmp-val" style={{ fontSize: "2.4rem" }}>+₹{topIpo.gmp}</div>
              <div className="gmp-label">GMP</div>
            </div>
          </div>
        </article>
      )}

      <div className="grid cols-2">
        {ipos.map((ipo, i) => <IpoCard key={ipo.name} ipo={ipo} index={i} />)}
      </div>
    </MarketNerveShell>
  );
}
