"use client";

import { motion } from "framer-motion";

function toState(on, warn = false) {
  if (warn) return "warn";
  return on ? "active" : "off";
}

export function LiveStatusStrip({ health }) {
  const capabilities = health?.capabilities ?? {};
  const marketStatus = health?.market_status ?? {};
  const pipelineStatus = health?.pipeline_status ?? {};

  const hasMarketFeed = typeof marketStatus === "object" && Object.keys(marketStatus).length > 0;
  const pipelineOk = (pipelineStatus.status || "").toLowerCase() === "success" || Number(pipelineStatus.signals_generated || 0) > 0;

  const cards = [
    {
      label: "Market Feed",
      value: hasMarketFeed ? "Streaming" : "Waiting",
      state: toState(hasMarketFeed, !hasMarketFeed),
    },
    {
      label: "Postgres DB",
      value: capabilities.persistence ? "Active" : "Offline",
      state: toState(!!capabilities.persistence),
    },
    {
      label: "Redis Stream",
      value: capabilities.real_time_signals ? "Active" : "Offline",
      state: toState(!!capabilities.real_time_signals),
    },
    {
      label: "Signals AI",
      value: capabilities.mistral_primary ? "Mistral Active" : "Fallback",
      state: toState(!!capabilities.mistral_primary, !capabilities.mistral_primary),
    },
    {
      label: "Narrative AI",
      value: capabilities.gemini_fallback ? "Gemini Active" : "Disabled",
      state: toState(!!capabilities.gemini_fallback, !capabilities.gemini_fallback),
    },
    {
      label: "Pipelines",
      value: pipelineOk ? "Running" : "Starting",
      state: toState(pipelineOk, !pipelineOk),
    },
  ];

  return (
    <div className="live-status-strip anim-fade-up">
      {cards.map((card, index) => (
        <motion.article
          key={card.label}
          className={`status-chip ${card.state}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, delay: index * 0.06 }}
          whileHover={{ y: -2, transition: { type: "spring", stiffness: 300, damping: 20 } }}
        >
          <div className="status-chip-top">
            <span className="status-chip-label">{card.label}</span>
            <span className={`status-ping ${card.state}`} />
          </div>
          <div className="status-chip-value">{card.value}</div>
        </motion.article>
      ))}
    </div>
  );
}
