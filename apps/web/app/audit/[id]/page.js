import { MarketNerveShell } from "../../../components/marketnerve-shell";
import { getAuditData } from "../../../lib/marketnerve-api.mjs";

export default async function AuditPage({ params }) {
  const { id } = await params;
  const audit = await getAuditData(id);
  const enrich = audit.enrichment_snapshot ?? {};
  const confMeta = audit.confidence_metadata ?? {};

  return (
    <MarketNerveShell
      eyebrow="Signal Audit Trail — Full Transparency"
      title={`AUDIT <span class="accent">${audit.ticker}</span>`}
      subtitle={`Signal ID: ${audit.signal_id ?? id}`}
    >
      {/* Signal summary hero */}
      <article className="panel hot corner-ornament" style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 14 }}>
          <span className="badge badge-neon">Verified Signal</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--text3)", marginLeft: "auto" }}>
            {audit.event_timestamp ? new Date(audit.event_timestamp).toLocaleString("en-IN") : ""}
          </span>
        </div>
        <p style={{ fontSize: "1.05rem", fontWeight: 500, lineHeight: 1.5, color: "var(--text)", marginBottom: 10 }}>
          {audit.output?.headline}
        </p>
        <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", lineHeight: 1.65, color: "var(--text2)", marginBottom: 14 }}>
          {audit.output?.summary}
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 10 }}>
          {(audit.input_snapshot?.sources ?? []).map((src) => (
            <span key={src} style={{ padding: "2px 10px", borderRadius: 2, fontFamily: "var(--font-mono)", fontSize: "0.62rem", background: "var(--neon-dim)", border: "1px solid var(--border2)", color: "var(--neon)" }}>
              {src}
            </span>
          ))}
        </div>
        {audit.disclaimer && (
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--text3)", marginTop: 8 }}>
            ⚠ {audit.disclaimer}
          </p>
        )}
      </article>

      <div className="grid cols-2">
        {/* Reasoning chain */}
        <article className="panel">
          <div className="section-header">
            <span className="badge badge-purple">Reasoning Chain</span>
            <span className="section-count">{(audit.reasoning_chain ?? []).length} steps</span>
          </div>
          <div className="reasoning-chain">
            {(audit.reasoning_chain ?? []).map((step, i) => (
              <div key={i} className="reasoning-step">
                <div className="step-num">{i + 1}</div>
                <p className="step-text">{step}</p>
              </div>
            ))}
          </div>
        </article>

        {/* Right column: enrichment + confidence */}
        <div className="grid">
          <article className="panel cyan">
            <div className="section-header">
              <span className="badge badge-cyan">Enrichment Snapshot</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
              {Object.entries(enrich).map(([key, val]) => {
                if (Array.isArray(val) || typeof val === "object") return null;
                return (
                  <div key={key}>
                    <div className="meta-cell-key" style={{ marginBottom: 3 }}>{key.replace(/_/g, " ")}</div>
                    <div className="meta-cell-val">{typeof val === "number" ? val.toFixed(2) : String(val)}</div>
                  </div>
                );
              })}
            </div>
            {enrich.tags && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 12 }}>
                {enrich.tags.map((t) => <span key={t} className="badge badge-neon" style={{ fontSize: "0.58rem" }}>{t}</span>)}
              </div>
            )}
          </article>

          <article className="panel">
            <div className="section-header">
              <span className="badge badge-amber">Confidence Metadata</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10, marginBottom: 14 }}>
              {Object.entries(confMeta).map(([key, val]) => {
                if (Array.isArray(val) || typeof val === "object") return null;
                return (
                  <div key={key}>
                    <div className="meta-cell-key" style={{ marginBottom: 3 }}>{key.replace(/_/g, " ")}</div>
                    <div className="meta-cell-val amber">{typeof val === "number" ? (val < 1 ? (val * 100).toFixed(1) + "%" : val.toFixed(2)) : String(val)}</div>
                  </div>
                );
              })}
            </div>
            {(confMeta.failure_contexts ?? []).length > 0 && (
              <>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.58rem", letterSpacing: "0.16em", textTransform: "uppercase", color: "var(--text3)", marginBottom: 8 }}>
                  Failure Contexts
                </div>
                {confMeta.failure_contexts.map((ctx) => (
                  <div key={ctx} className="risk-flag" style={{ marginBottom: 6 }}>
                    <span style={{ color: "var(--red)" }}>⚠</span>
                    <p>{ctx}</p>
                  </div>
                ))}
              </>
            )}
          </article>
        </div>
      </div>
    </MarketNerveShell>
  );
}
