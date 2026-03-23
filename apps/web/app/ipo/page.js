import { IpoCard, MarketNerveShell } from "../../components/marketnerve-shell";
import { getIpoData } from "../../lib/marketnerve-api.mjs";

export default async function IpoPage() {
  const ipos = await getIpoData();

  const topIpo = ipos[0];

  return (
    <MarketNerveShell
      eyebrow="Primary Markets"
      title="IPO Intelligence"
      subtitle="Live GMP, subscription tracking, allotment odds, and plain-English risk assessment."
    >
      {/* Top IPO highlight */}
      {topIpo && (
        <article className="panel hero-panel-secondary" style={{ marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
            <span className="chip chip-amber">🔥 Hottest IPO</span>
            <span className="small mono text-faint">{topIpo.demand_label}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 20 }}>
            <div>
              <h2 style={{ fontSize: "1.4rem", marginBottom: 8 }}>{topIpo.name}</h2>
              <p className="subtle">{topIpo.summary}</p>
            </div>
            <div className="gmp-badge" style={{ flexShrink: 0 }}>
              <span className="gmp-badge__value">+₹{topIpo.gmp}</span>
              <span className="gmp-badge__label">GMP</span>
            </div>
          </div>
          <div className="meta-grid" style={{ marginTop: 16 }}>
            <div className="meta-item">
              <span className="meta-item__key">Subscription</span>
              <span className="meta-item__val text-amber">{topIpo.subscription_multiple}×</span>
            </div>
            <div className="meta-item">
              <span className="meta-item__key">Allotment Odds</span>
              <span className="meta-item__val">{Math.round(topIpo.allotment_probability * 100)}%</span>
            </div>
            <div className="meta-item">
              <span className="meta-item__key">Price</span>
              <span className="meta-item__val">{topIpo.cutoff_price ? `₹${topIpo.cutoff_price}` : "—"}</span>
            </div>
            <div className="meta-item">
              <span className="meta-item__key">Listing</span>
              <span className="meta-item__val">{topIpo.listing_date ?? "—"}</span>
            </div>
          </div>
        </article>
      )}

      <section className="grid columns-2">
        {ipos.map((ipo) => (
          <IpoCard key={ipo.name} ipo={ipo} />
        ))}
      </section>
    </MarketNerveShell>
  );
}
