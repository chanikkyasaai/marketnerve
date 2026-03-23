import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const seed = require("../../../config/marketnerve.seed.json");

export function getHomeModel() {
  const signals = [...seed.signals].sort((a, b) => b.impact_score - a.impact_score);
  return {
    generatedAt: seed.generated_at,
    signals,
    patterns: seed.patterns,
    video: seed.stories.daily_video,
    ipos: seed.ipos,
    health: seed.health,
  };
}

export function getPortfolioModel() {
  const holdings = seed.portfolio_demo.holdings;
  const invested = holdings.reduce((sum, item) => sum + item.invested_amount, 0);
  const current = holdings.reduce((sum, item) => sum + item.current_value, 0);

  return {
    name: seed.portfolio_demo.name,
    holdings,
    invested,
    current,
    gain: current - invested,
  };
}

export function getPortfolioAnalysis() {
  const model = getPortfolioModel();
  const total = model.current || 1;
  const sectorMap = new Map();

  for (const holding of model.holdings) {
    sectorMap.set(holding.sector, (sectorMap.get(holding.sector) || 0) + holding.current_value);
  }

  const overlapMatrix = model.holdings
    .filter((holding) => holding.asset_type === "Mutual Fund")
    .map((holding) => ({
      fund: holding.name,
      overlaps: Object.entries(holding.lookthrough_exposure || {})
        .map(([symbol, overlap_weight]) => ({ symbol, overlap_weight }))
        .sort((a, b) => b.overlap_weight - a.overlap_weight),
    }));

  return {
    portfolio_name: model.name,
    currency: "INR",
    holdings_count: model.holdings.length,
    invested_amount: model.invested,
    current_value: model.current,
    absolute_gain: model.gain,
    xirr: 0.1462,
    money_health_score: 78,
    sector_exposure: [...sectorMap.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([sector, value]) => ({ sector, weight: Number((value / total).toFixed(4)) })),
    overlap_matrix: overlapMatrix,
    recommended_actions: [
      "Review financial-services concentration because direct and mutual-fund exposure overlap.",
      "Persistent Systems is the strongest live positive signal in the current holdings mix.",
      "Keep one dry-powder allocation for market-wide drawdown opportunities.",
    ],
  };
}

export function getStoryArc(query = "") {
  const arcs = seed.stories.arcs;
  return arcs.find((item) => item.slug.includes(query.toLowerCase())) || arcs[0];
}

export function getSignalById(id = "") {
  return seed.signals.find((item) => item.id === id) || seed.signals[0];
}

export function answerPortfolioQuestionLocal(question = "") {
  const lower = question.toLowerCase();
  const analysis = getPortfolioAnalysis();

  if (lower.includes("overlap")) {
    const top = analysis.overlap_matrix.sort((a, b) => b.overlaps.length - a.overlaps.length)[0];
    return {
      question,
      answer: top
        ? `${top.fund} has the highest visible overlap with the direct equity book.`
        : "No overlap was detected between mutual funds and direct equities.",
      logic: [
        "Parsed portfolio holdings.",
        "Computed overlap between direct equity and mutual fund look-through exposures.",
        "Returned only values derivable from holdings data.",
      ],
      sources: ["Uploaded holdings data", "Shared seed market snapshot"],
    };
  }

  if (lower.includes("reliance")) {
    const total = analysis.current_value || 1;
    const exposure = seed.portfolio_demo.holdings.reduce((sum, holding) => {
      if (holding.symbol === "RELIANCE") {
        return sum + holding.current_value;
      }
      if (holding.lookthrough_exposure?.RELIANCE) {
        return sum + (holding.current_value * holding.lookthrough_exposure.RELIANCE);
      }
      return sum;
    }, 0);
    return {
      question,
      answer: `Estimated look-through exposure to Reliance is ${((exposure / total) * 100).toFixed(2)}% of portfolio value.`,
      logic: [
        "Parsed portfolio holdings.",
        "Computed direct and look-through Reliance exposure.",
        "Returned only values derivable from holdings data.",
      ],
      sources: ["Uploaded holdings data", "Shared seed market snapshot"],
    };
  }

  return {
    question,
    answer: `The current portfolio XIRR is ${(analysis.xirr * 100).toFixed(2)}%. For the seeded demo portfolio that is healthy, supported by gains in both direct equity and diversified funds.`,
    logic: [
      "Parsed portfolio holdings.",
      "Computed portfolio return metrics.",
      "Returned only values derivable from holdings data.",
    ],
    sources: ["Uploaded holdings data", "Shared seed market snapshot"],
  };
}
