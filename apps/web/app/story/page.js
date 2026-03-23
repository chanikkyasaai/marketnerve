import { MarketNerveShell, StoryArcCard } from "../../components/marketnerve-shell";
import { getLatestVideoData, getStoryArcData } from "../../lib/marketnerve-api.mjs";

const KNOWN_ARCS = [
  { slug: "zomato", label: "Zomato Profitability" },
  { slug: "hdfc", label: "HDFC Merger" },
  { slug: "adani", label: "Adani Recovery" },
  { slug: "nifty-it", label: "Nifty IT Rally" },
  { slug: "ipo", label: "IPO Wave 2026" },
];

export default async function StoryPage({ searchParams }) {
  const params = await searchParams;
  const query = params?.query || "zomato";
  const [video, leadArc] = await Promise.all([getLatestVideoData(), getStoryArcData(query)]);

  return (
    <MarketNerveShell
      eyebrow="Story Engine"
      title="Market Narrative Intelligence"
      subtitle="Autonomous daily wrap, interactive story arcs, and AI-driven filing classification."
    >
      {/* Daily Video card */}
      <article className="panel hero-panel-secondary" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
          <span className="chip chip-amber">📹 Today's Market Wrap</span>
        </div>
        <div className="split" style={{ gap: 24 }}>
          <div>
            <h2 style={{ fontSize: "1.3rem", marginBottom: 10 }}>{video.title}</h2>
            <p className="subtle small">{video.summary}</p>
            <div className="meta-grid" style={{ marginTop: 14 }}>
              <div className="meta-item">
                <span className="meta-item__key">Duration</span>
                <span className="meta-item__val">{video.duration_seconds}s</span>
              </div>
              <div className="meta-item">
                <span className="meta-item__key">Formats</span>
                <span className="meta-item__val">{(video.formats ?? []).join(", ")}</span>
              </div>
            </div>
          </div>
          <div>
            <p className="small mono text-faint" style={{ marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.06em" }}>Script Outline</p>
            <div className="timeline">
              {(video.script_outline ?? []).map((step, i) => (
                <div key={i} className="timeline-item">
                  <span className="timeline-date">Step {i + 1}</span>
                  <span className="timeline-label small">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </article>

      {/* Story Arc Section */}
      <div className="split">
        <div>
          <section className="panel" style={{ marginBottom: 18 }}>
            <form action="/story" method="get">
              <div className="filters-grid" style={{ gridTemplateColumns: "1fr auto" }}>
                <label>
                  Search story arc
                  <input name="query" defaultValue={query} placeholder="zomato, hdfc, adani…" />
                </label>
                <button type="submit" style={{ width: "auto", marginTop: 24, padding: "12px 24px" }}>Load →</button>
              </div>
            </form>
            <div className="tags" style={{ marginTop: 14 }}>
              {KNOWN_ARCS.map((arc) => (
                <a key={arc.slug} href={`/story?query=${arc.slug}`} className="tag" style={{ cursor: "pointer" }}>
                  {arc.label}
                </a>
              ))}
            </div>
          </section>
          <StoryArcCard arc={leadArc} />
        </div>

        <div className="panel">
          <p className="chip chip-purple" style={{ marginBottom: 14 }}>Arc Details</p>
          <h3 style={{ marginBottom: 8 }}>{leadArc.title}</h3>
          <p className="subtle small" style={{ marginBottom: 16 }}>{leadArc.thesis}</p>
          <div>
            <p className="small mono text-faint" style={{ marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.06em" }}>What to watch next</p>
            {(leadArc.what_to_watch_next ?? []).map((item) => (
              <div key={item} className="action-item" style={{ marginBottom: 8 }}>
                <span>→</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 18, paddingTop: 18, borderTop: "1px solid var(--border)" }}>
            <p className="small mono text-faint" style={{ marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>Sentiment</p>
            <span className="chip chip-green">{leadArc.sentiment}</span>
            <span className="mono text-green" style={{ marginLeft: 12, fontSize: "1.2rem", fontWeight: 700 }}>
              {Math.round((leadArc.sentiment_score ?? 0.5) * 100)}%
            </span>
          </div>
        </div>
      </div>
    </MarketNerveShell>
  );
}
