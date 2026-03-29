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
  // Live data only - no seed fallback
  return payload?.items || [];
}

export async function getSignalsPerformance() {
  return (await safeFetchJson("/api/signals/performance")) || {
    horizons: { t1: 0, t5: 0, t30: 0 },
    by_signal_type: [],
    sample_size: 0,
    method: "confidence_weighted_backtest_projection",
  };
}

export async function getSignalsCalibration() {
  return (await safeFetchJson("/api/signals/calibration")) || {
    bins: [],
    mean_absolute_error: 0,
    sample_size: 0,
    method: "confidence_vs_backtest_winrate_bucketed",
  };
}

export async function getPatternsData({ patternType = "", ticker = "" } = {}) {
  const search = new URLSearchParams();
  if (patternType) search.set("pattern_type", patternType);
  if (ticker) search.set("ticker", ticker);
  const payload = await safeFetchJson(`/api/patterns/scan?${search.toString()}`);
  // Live data only - no seed fallback
  return payload?.items || [];
}

export async function getHealthData() {
  // Live data only - no seed fallback
  return (await safeFetchJson("/api/health")) || {
    market_status: {},
    data_freshness_minutes: 0,
    total_signals_processed: 0,
    api_p95_ms: 0,
    pipeline_status: {},
    capabilities: {
      persistence: false,
      real_time_signals: false,
      ai_enrichment: false,
      mistral_primary: false,
      gemini_fallback: false,
    },
  };
}

export async function getIpoData() {
  const payload = await safeFetchJson("/api/ipo/active");
  // Live data only - no seed fallback
  return payload?.items || [];
}

export async function getLatestVideoData() {
  // Live data only - no seed fallback
  return (await safeFetchJson("/api/story/video/latest")) || { title: "Market data loading...", summary: "", script_outline: [] };
}

export async function generateLatestVideo() {
  return (await safeFetchJson("/api/story/video/generate", { method: "POST", body: JSON.stringify({}) })) || null;
}

export async function getStoryArcData(query = "") {
  return (await safeFetchJson(`/api/story/arc/${encodeURIComponent(query || "zomato-profitability-journey")}`)) || null;
}

export async function getAuditData(id) {
  // Live data only - no seed fallback
  return (await safeFetchJson(`/api/audit/${encodeURIComponent(id)}`)) || null;
}

export async function analyzePortfolio(payload = { use_demo_data: false }) {
  // Live data only - require CSV upload, no seed fallback
  const response = await safeFetchJson("/api/portfolio/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return response || null;
}

export async function queryPortfolio(payload) {
  // Live data only - no seed fallback
  return (
    (await safeFetchJson("/api/portfolio/query", {
      method: "POST",
      body: JSON.stringify(payload),
    })) || null
  );
}


export async function sendChatMessage(question) {
  return (
    (await safeFetchJson("/api/chat", {
      method: "POST",
      body: JSON.stringify({ question }),
    })) ?? { answer: null, sources: [] }
  );
}
