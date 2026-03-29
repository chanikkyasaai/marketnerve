"use client";

import { useMemo, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export function StoryVideoControl({ initialRenderStatus }) {
  const [status, setStatus] = useState(initialRenderStatus || {});
  const [loading, setLoading] = useState(false);

  const canTrigger = useMemo(() => {
    const state = status?.state || "idle";
    return state !== "queued" && state !== "rendering";
  }, [status]);

  async function refreshStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/story/video/latest`, { cache: "no-store" });
      if (!res.ok) return;
      const payload = await res.json();
      setStatus(payload?.render_status || {});
    } catch {
      // no-op
    }
  }

  async function runGenerate() {
    if (loading) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/story/video/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (res.ok) {
        const payload = await res.json();
        setStatus(payload?.render_status || {});
      }

      // Poll for state transitions queued -> rendering -> ready
      for (let i = 0; i < 8; i++) {
        await new Promise((resolve) => setTimeout(resolve, 1800));
        await refreshStatus();
      }
    } finally {
      setLoading(false);
    }
  }

  const state = status?.state || "idle";
  const progress = Number(status?.progress_pct || 0);
  const eta = Number(status?.estimated_seconds_remaining || 0);

  return (
    <div style={{ marginTop: 12, padding: "10px 12px", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface-1)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
        <button className="war-btn" type="button" onClick={runGenerate} disabled={!canTrigger || loading}>
          {loading ? "Generating…" : "Generate Today's Wrap Now"}
        </button>
        <span className="badge badge-amber">{state}</span>
        <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)" }}>
          ETA {eta}s
        </span>
      </div>
      <div style={{ height: 4, background: "var(--surface-2)", borderRadius: 2, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg, var(--amber), var(--accent))", borderRadius: 2, transition: "width 0.35s ease" }} />
      </div>
    </div>
  );
}
