import {
  answerPortfolioQuestionLocal,
  getHomeModel,
  getPortfolioAnalysis,
  getSignalById,
  getStoryArc,
} from "./marketnerve-data.mjs";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function safeFetchJson(path, options) {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return await response.json();
  } catch {
    return null;
  }
}

export async function getSignalsData({ sector = "", minConfidence = "" } = {}) {
  const search = new URLSearchParams();
  if (sector) search.set("sector", sector);
  if (minConfidence) search.set("min_confidence", minConfidence);
  const payload = await safeFetchJson(`/api/signals?${search.toString()}`);
  return payload?.items || getHomeModel().signals;
}

export async function getPatternsData({ patternType = "", ticker = "" } = {}) {
  const search = new URLSearchParams();
  if (patternType) search.set("pattern_type", patternType);
  if (ticker) search.set("ticker", ticker);
  const payload = await safeFetchJson(`/api/patterns/scan?${search.toString()}`);
  return payload?.items || getHomeModel().patterns;
}

export async function getHealthData() {
  return (await safeFetchJson("/api/health")) || getHomeModel().health;
}

export async function getIpoData() {
  const payload = await safeFetchJson("/api/ipo/active");
  return payload?.items || getHomeModel().ipos;
}

export async function getLatestVideoData() {
  return (await safeFetchJson("/api/story/video/latest")) || getHomeModel().video;
}

export async function getStoryArcData(query = "") {
  return (await safeFetchJson(`/api/story/arc/${encodeURIComponent(query || "zomato")}`)) || getStoryArc(query);
}

export async function getAuditData(id) {
  return (await safeFetchJson(`/api/audit/${encodeURIComponent(id)}`)) || {
    signal_id: id,
    ...getSignalById(id),
    input_snapshot: {
      sources: getSignalById(id).sources,
      sector: getSignalById(id).sector,
      age_minutes: getSignalById(id).age_minutes,
    },
    reasoning_chain: getSignalById(id).reasoning_steps,
    output: {
      headline: getSignalById(id).headline,
      summary: getSignalById(id).summary,
      watch_items: getSignalById(id).watch_items,
    },
    disclaimer: "Historical pattern data, not a recommendation.",
  };
}

export async function analyzePortfolio(payload = { use_demo_data: true }) {
  return (
    (await safeFetchJson("/api/portfolio/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    })) || getPortfolioAnalysis()
  );
}

export async function queryPortfolio(payload) {
  return (
    (await safeFetchJson("/api/portfolio/query", {
      method: "POST",
      body: JSON.stringify(payload),
    })) || answerPortfolioQuestionLocal(payload.question)
  );
}
