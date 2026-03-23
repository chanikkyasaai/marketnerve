import { MarketNerveShell } from "../../../components/marketnerve-shell";
import { getAuditData } from "../../../lib/marketnerve-api.mjs";

export default async function AuditPage({ params }) {
  const { id } = await params;
  const audit = await getAuditData(id);

  return (
    <MarketNerveShell
      eyebrow="Audit Trail"
      title={`Signal: ${audit.ticker}`}
      subtitle="Full reasoning chain, input snapshot, enrichment data, and confidence metadata."
    >
      {/* Summary Panel */}
      <article className="panel hero-panel-lead" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
          <span className="chip chip-green">Verified Signal</span>
          <span className="ticker">{audit.signal_id}</span>
        </div>
        <p className="headline-text" style={{ marginBottom: 10 }}>{audit.output?.headline}</p>
        <p className="subtle small">{audit.output?.summary}</p>
        <div className="tags" style={{ marginTop: 14 }}>
          {(audit.input_snapshot?.sources ?? []).map((src) => (
            <span key={src} className="source-tag">{src}</span>
          ))}
        </div>
        {audit.disclaimer && (
          <p className="small text-faint mono" style={{ marginTop: 12 }}>⚠ {audit.disclaimer}</p>
        )}
      </article>

      <div className="grid columns-2">
        {/* Reasoning Chain */}
        <article className="panel">
          <p className="chip chip-purple" style={{ marginBottom: 16 }}>Reasoning Chain</p>
          <div>
            {(audit.reasoning_chain ?? []).map((step, i) => (
              <div key={i} className="reasoning-step">
                <div className="step-number">{i + 1}</div>
                <p className="small" style={{ paddingTop: 4 }}>{step}</p>
              </div>
            ))}
          </div>
        </article>

        {/* Enrichment Snapshot */}
        <div className="grid">
          <article className="panel">
            <p className="chip chip-amber" style={{ marginBottom: 14 }}>Enrichment Snapshot</p>
            <div className="meta-grid">
              {audit.enrichment_snapshot && Object.entries(audit.enrichment_snapshot).map(([key, val]) => {
                if (Array.isArray(val)) return null;
                return (
                  <div key={key} className="meta-item">
                    <span className="meta-item__key">{key.replace(/_/g, " ")}</span>
                    <span className="meta-item__val">{typeof val === "number" ? val.toFixed(2) : String(val)}</span>
                  </div>
                );
              })}
            </div>
            {audit.enrichment_snapshot?.tags && (
              <div className="tags" style={{ marginTop: 12 }}>
                {audit.enrichment_snapshot.tags.map((t) => <span key={t} className="tag">{t}</span>)}
              </div>
            )}
          </article>

          <article className="panel">
            <p className="chip chip-green" style={{ marginBottom: 14 }}>Confidence Metadata</p>
            <div className="meta-grid">
              {audit.confidence_metadata && Object.entries(audit.confidence_metadata).map(([key, val]) => {
                if (Array.isArray(val)) return null;
                return (
                  <div key={key} className="meta-item">
                    <span className="meta-item__key">{key.replace(/_/g, " ")}</span>
                    <span className="meta-item__val">{typeof val === "number" ? val.toFixed ? val.toFixed(3) : val : String(val)}</span>
                  </div>
                );
              })}
            </div>
            {audit.confidence_metadata?.failure_contexts && (
              <div style={{ marginTop: 12 }}>
                <p className="small mono text-faint" style={{ marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>Failure Contexts</p>
                {audit.confidence_metadata.failure_contexts.map((ctx) => (
                  <div key={ctx} className="risk-flag" style={{ marginBottom: 6 }}>
                    <span>⚠</span><span className="small">{ctx}</span>
                  </div>
                ))}
              </div>
            )}
          </article>
        </div>
      </div>
    </MarketNerveShell>
  );
}
