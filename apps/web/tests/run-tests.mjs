import assert from "node:assert/strict";

import {
  answerPortfolioQuestionLocal,
  getHomeModel,
  getPortfolioAnalysis,
  getPortfolioModel,
  getStoryArc,
} from "../lib/marketnerve-data.mjs";

function run(name, fn) {
  try {
    fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    console.error(error);
    process.exitCode = 1;
  }
}

run("home model exposes ranked signals and health data", () => {
  const model = getHomeModel();
  assert.ok(model.signals.length >= 3);
  assert.ok(model.signals[0].impact_score >= model.signals[1].impact_score);
  assert.equal(model.health.status, "healthy");
});

run("portfolio model computes positive gain", () => {
  const model = getPortfolioModel();
  assert.ok(model.current > model.invested);
  assert.ok(model.gain > 0);
});

run("story arc lookup falls back gracefully", () => {
  const arc = getStoryArc("unknown");
  assert.ok(arc.title);
  assert.ok(arc.events.length >= 1);
});

run("portfolio analysis exposes overlap matrix", () => {
  const analysis = getPortfolioAnalysis();
  assert.ok(analysis.overlap_matrix.length >= 1);
  assert.ok(analysis.sector_exposure.length >= 1);
});

run("local portfolio reasoning returns grounded text", () => {
  const response = answerPortfolioQuestionLocal("How exposed am I to a Reliance Industries earnings miss?");
  assert.ok(response.answer.includes("Reliance"));
  assert.ok(response.logic.length >= 2);
});
