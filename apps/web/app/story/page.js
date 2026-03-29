import { MarketNerveShell, StoryArcCard } from "../../components/marketnerve-shell";
import { StoryVideoControl } from "../../components/story-video-control";
import { getLatestVideoData, getStoryArcData, getHealthData } from "../../lib/marketnerve-api.mjs";

const ARCS = [
  { slug: "zomato", label: "Zomato", color: "var(--green)" },
  { slug: "hdfc", label: "HDFC Merger", color: "var(--accent)" },
  { slug: "adani", label: "Adani", color: "var(--amber)" },
  { slug: "nifty-it", label: "Nifty IT", color: "var(--cyan)" },
  { slug: "ipo", label: "IPO Wave 2026", color: "var(--purple)" },
];

export default async function StoryPage({ searchParams }) {
  const params = await searchParams;
  const query = params?.query || "zomato";
  const [video, arc, health] = await Promise.all([
    getLatestVideoData(),
    getStoryArcData(query),
    getHealthData(),
  ]);
  const allArcs = await Promise.all(ARCS.map((a) => getStoryArcData(a.slug)));

  return (
    <MarketNerveShell
      marketStatus={health.market_status}
      eyebrow="Story Engine · AI Narrative Intelligence"
      title={`Narrative <span class="accent">Intel</span>`}
      subtitle="Event-driven story arcs · Filing-based classification · AI-generated market narratives"
    >
      {/* Video wrap panel */}
      <article className="panel amber-panel" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 16 }}>
          <span className="badge badge-amber">Today's Market Wrap</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-3)", marginLeft: "auto" }}>
            {(video.formats ?? []).join(" · ")}
          </span>
        </div>
        <div className="grid cols-2" style={{ gap: 24 }}>
          <div>
            <div style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: "18px", color: "var(--text)", marginBottom: 10, letterSpacing: "-0.01em", lineHeight: 1.3 }}>
              {video.title}
            </div>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.7, color: "var(--text-2)" }}>
              {video.summary}
            </p>

            <div style={{ marginTop: 14, padding: "10px 12px", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface-1)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                  Render Status
                </span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--amber)", fontWeight: 700 }}>
                  {video?.render_status?.state || "queued"}
                </span>
              </div>
              <div style={{ height: 4, background: "var(--surface-2)", borderRadius: 2, overflow: "hidden", marginBottom: 6 }}>
                <div style={{ height: "100%", width: `${video?.render_status?.progress_pct || 0}%`, background: "linear-gradient(90deg, var(--amber), var(--accent))", borderRadius: 2 }} />
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)" }}>
                {video?.render_status?.progress_pct || 0}% complete · ETA {video?.render_status?.estimated_seconds_remaining || 0}s
              </div>
            </div>
            <StoryVideoControl initialRenderStatus={video?.render_status || {}} />
          </div>
          <div>
            <p style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: 12 }}>
              Script Outline
            </p>
            {(video.script_outline ?? []).map((step, i) => (
              <div key={i} style={{ display: "flex", gap: 10, marginBottom: 8, alignItems: "flex-start" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--amber)", flexShrink: 0, marginTop: 2, fontWeight: 700 }}>
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-2)", lineHeight: 1.55 }}>{step}</span>
              </div>
            ))}

            {(video.scene_plan ?? []).length > 0 ? (
              <div style={{ marginTop: 14 }}>
                <p style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: 10 }}>
                  Scene Plan
                </p>
                {(video.scene_plan ?? []).slice(0, 6).map((scene) => (
                  <div key={scene.scene} style={{ display: "flex", justifyContent: "space-between", gap: 10, padding: "6px 8px", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface-0)", marginBottom: 6 }}>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-2)" }}>{scene.title}</span>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)", whiteSpace: "nowrap" }}>{scene.start_second}s–{scene.end_second}s</span>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </article>

      {/* Arc tabs + content */}
      <div style={{ display: "flex", gap: 6, marginBottom: 20, flexWrap: "wrap" }}>
        {ARCS.map((a) => {
          const isActive = query.includes(a.slug.substring(0, 4));
          return (
            <a key={a.slug} href={`/story?query=${a.slug}`} style={{
              padding: "6px 14px", borderRadius: 8, textDecoration: "none",
              fontFamily: "var(--font-mono)", fontSize: "12px", letterSpacing: "0.04em",
              border: `1px solid ${isActive ? a.color : "var(--border)"}`,
              color: isActive ? a.color : "var(--text-3)",
              background: isActive ? `rgba(${a.color === "var(--green)" ? "34,197,94" : a.color === "var(--accent)" ? "91,106,240" : a.color === "var(--amber)" ? "245,158,11" : a.color === "var(--cyan)" ? "6,182,212" : "168,85,247"},0.1)` : "transparent",
              transition: "all 0.15s",
            }}>
              {a.label}
            </a>
          );
        })}
      </div>

      <div className="split-wide">
        <div>
          <StoryArcCard arc={arc} index={0} />
        </div>

        <article className="panel">
          <div style={{ marginBottom: 16 }}>
            <span className="badge badge-purple">Arc Analysis</span>
          </div>
          <h3 style={{ fontFamily: "var(--font-ui)", fontWeight: 700, fontSize: "16px", color: "var(--text)", marginBottom: 8, letterSpacing: "-0.01em" }}>
            {arc.title}
          </h3>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.7, color: "var(--text-2)", marginBottom: 16 }}>
            {arc.thesis}
          </p>

          {/* Sentiment gauge */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.08em" }}>Sentiment Score</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--green)", fontWeight: 700 }}>
                {Math.round((arc.sentiment_score ?? 0.5) * 100)}%
              </span>
            </div>
            <div style={{ height: 4, background: "var(--surface-2)", borderRadius: 2, overflow: "hidden" }}>
              <div style={{
                height: "100%",
                width: `${Math.round((arc.sentiment_score ?? 0.5) * 100)}%`,
                background: "linear-gradient(90deg, var(--green), var(--accent))",
                borderRadius: 2,
                transition: "width 0.6s ease",
              }} />
            </div>
          </div>

          <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 10 }}>
            What to Watch
          </div>
          {(arc.what_to_watch_next ?? []).map((item) => (
            <div key={item} className="action-item">
              <span style={{ color: "var(--accent)", flexShrink: 0 }}>→</span>
              <p>{item}</p>
            </div>
          ))}
        </article>
      </div>

      {/* All arcs grid */}
      <div style={{ marginTop: 32 }}>
        <div className="section-header">
          <span style={{ color: "var(--purple)", fontSize: 12 }}>▲</span>
          <span className="section-title">All Story Arcs</span>
          <span className="section-count">{allArcs.length} narratives</span>
        </div>
        <div className="grid cols-3">
          {allArcs.map((a, i) => <StoryArcCard key={a.slug} arc={a} index={i} />)}
        </div>
      </div>
    </MarketNerveShell>
  );
}
