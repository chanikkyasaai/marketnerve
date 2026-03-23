import { MarketNerveShell, StoryArcCard } from "../../components/marketnerve-shell";
import { getLatestVideoData, getStoryArcData } from "../../lib/marketnerve-api.mjs";

const ARCS = [
  { slug: "zomato", label: "Zomato" },
  { slug: "hdfc", label: "HDFC Merger" },
  { slug: "adani", label: "Adani" },
  { slug: "nifty-it", label: "Nifty IT" },
  { slug: "ipo", label: "IPO Wave" },
];

export default async function StoryPage({ searchParams }) {
  const params = await searchParams;
  const query = params?.query || "zomato";
  const [video, arc] = await Promise.all([getLatestVideoData(), getStoryArcData(query)]);

  return (
    <MarketNerveShell
      eyebrow="Story Engine — Autonomous Market Media"
      title={`NARRATIVE <span class="accent">INTEL</span>`}
      subtitle="Daily video wraps · AI story arcs · Filing-driven event classification"
    >
      {/* Video panel */}
      <article className="panel amber-panel corner-ornament" style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 14 }}>
          <span className="badge badge-amber">📹 Today's Market Wrap</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--text3)", marginLeft: "auto" }}>
            {(video.formats ?? []).join(" · ")}
          </span>
        </div>
        <div className="grid cols-2" style={{ gap: 24 }}>
          <div>
            <div style={{ fontFamily: "var(--font-display)", fontSize: "1.6rem", letterSpacing: "0.04em", color: "var(--text)", marginBottom: 10 }}>
              {video.title}
            </div>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.74rem", lineHeight: 1.65, color: "var(--text2)" }}>
              {video.summary}
            </p>
          </div>
          <div>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.58rem", letterSpacing: "0.16em", textTransform: "uppercase", color: "var(--text3)", marginBottom: 12 }}>
              Script Outline
            </p>
            {(video.script_outline ?? []).map((step, i) => (
              <div key={i} style={{ display: "flex", gap: 10, marginBottom: 8, alignItems: "flex-start" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: "var(--amber)", flexShrink: 0, marginTop: 1 }}>{i + 1}.</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--text2)", lineHeight: 1.5 }}>{step}</span>
              </div>
            ))}
          </div>
        </div>
      </article>

      {/* Arc selector + display */}
      <div className="split-wide">
        <div>
          <article className="panel" style={{ marginBottom: 16 }}>
            <form action="/story" method="get" style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
              <div className="field-group" style={{ flex: 1 }}>
                <label className="field-label">Search Arc</label>
                <input name="query" defaultValue={query} placeholder="zomato, hdfc, adani…" />
              </div>
              <button type="submit" className="war-btn">Load →</button>
            </form>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 12 }}>
              {ARCS.map((a) => (
                <a key={a.slug} href={`/story?query=${a.slug}`}
                  style={{ padding: "4px 12px", border: "1px solid var(--border)", borderRadius: 2, fontFamily: "var(--font-mono)", fontSize: "0.62rem", color: query.includes(a.slug.substring(0, 4)) ? "var(--neon)" : "var(--text3)", background: query.includes(a.slug.substring(0, 4)) ? "var(--neon-glow)" : "transparent", letterSpacing: "0.08em", textDecoration: "none" }}>
                  {a.label}
                </a>
              ))}
            </div>
          </article>
          <StoryArcCard arc={arc} index={0} />
        </div>

        <article className="panel">
          <div className="section-header">
            <span className="badge badge-purple">Arc Details</span>
            <span style={{ fontFamily: "var(--font-display)", fontSize: "1.6rem", color: "var(--neon)", marginLeft: "auto" }}>
              {Math.round((arc.sentiment_score ?? 0.5) * 100)}%
            </span>
          </div>
          <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.3rem", letterSpacing: "0.05em", color: "var(--text)", marginBottom: 8 }}>{arc.title}</h3>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.74rem", lineHeight: 1.65, color: "var(--text2)", marginBottom: 16 }}>{arc.thesis}</p>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.58rem", letterSpacing: "0.16em", textTransform: "uppercase", color: "var(--text3)", marginBottom: 10 }}>What to Watch</div>
          {(arc.what_to_watch_next ?? []).map((item) => (
            <div key={item} className="action-item" style={{ marginBottom: 6 }}>
              <span style={{ color: "var(--neon)" }}>→</span>
              <p>{item}</p>
            </div>
          ))}
        </article>
      </div>
    </MarketNerveShell>
  );
}
