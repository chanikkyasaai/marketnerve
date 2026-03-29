# MarketNerve Product Blueprint

## Executive Summary

MarketNerve is an intelligence operating layer built for Indian retail investing workflows.
Instead of offering static market snapshots, it continuously transforms fragmented data into ranked opportunities, technical conviction signals, portfolio-aware reasoning, and narrative market context.

The system combines deterministic analytics, statistical scoring, and LLM-assisted explanation under a strict evidence-first approach.

## 1. Problem Statement

India has over 14 crore demat accounts, but retail investors still struggle with:

1. Information overload without prioritization
2. Delayed interpretation of corporate and flow events
3. Technical analysis complexity without stock-specific context
4. Portfolio decisions based on intuition instead of measurable diagnostics
5. Low-trust guidance due to weak source traceability

The market does not need another dashboard. It needs an actionable intelligence layer.

## 2. Mission and Product Positioning

Mission:

- Help Indian investors make faster, better, and more explainable decisions using machine-assisted intelligence.

Positioning:

- Not a data terminal
- Not a headline summarizer
- Not generic AI chat
- A decision-intelligence system with ranking, confidence, calibration, and auditability

## 3. Product Objectives

1. Surface missed opportunities with ranking and urgency
2. Explain technical and event-based setups in plain language
3. Offer portfolio-specific reasoning, not generic market answers
4. Provide source-cited AI output with confidence metadata
5. Maintain reliability under unstable upstream feeds

## 4. Design and Decision Framework

### 4.1 System-level principles

1. Signal over feed volume
2. Explainability before complexity
3. Auditability by default
4. Progressive reliability with graceful fallback
5. Consistent response contracts for every module

### 4.2 User-facing principles

1. Every important output should answer: what happened, why it matters, and what to watch next
2. Every AI response should show confidence and evidence
3. Every score should map to observable metrics
4. Loading should communicate system state, not just spinners

## 5. End-to-End Product Modules

### 5.1 Opportunity Radar

Purpose:

- Rank opportunity candidates using anomaly, confidence, and historical profile.

Inputs:

- Signal candidates, filing events, flow shifts, technical anomalies.

Outputs:

- Actionable score
- Confidence band
- Evidence chips
- Direct audit trail links

### 5.2 Chart Pattern Intelligence

Purpose:

- Detect and explain technical setups with stock-level context.

Key patterns:

- Golden Cross
- Death Cross
- RSI regime signals
- Volume breakouts
- 52-week breakout and support behavior

Outputs:

- Pattern narrative
- Backtest win-rate and sample size
- Risk and watch flags

### 5.3 Market ChatGPT Next Gen

Purpose:

- Offer grounded, source-cited answers using live module context.

Characteristics:

- Confidence, highlights, citations, and sources
- Portfolio-aware context injection
- Structured JSON contract to reduce output drift

### 5.4 Portfolio Lens

Purpose:

- Turn holdings CSV into diagnostics and decision support.

Capabilities:

- Holdings normalization
- Sector and concentration diagnostics
- Health dimensions and score
- Overlap and benchmark context
- Ask-your-portfolio reasoning

### 5.5 Story Engine and Video Layer

Purpose:

- Convert market state into narrative intelligence and daily wrap generation workflow.

Outputs:

- Story arcs
- Video script outline
- Scene plan with timestamps
- Render lifecycle state (queued, rendering, ready)

### 5.6 IPO Intelligence

Purpose:

- Translate subscription and demand behavior into practical retail framing.

Outputs:

- Demand labels
- GMP-aware context
- Allotment probability framing
- Risk-level tagging

## 6. Data Sources and Data Contracts

### 6.1 External data inputs

1. NSE announcements and selected market endpoints
2. BSE corporate disclosures and SAST-related feeds
3. yfinance OHLCV and index views
4. Institutional flow context (FII and DII)

### 6.2 Internal datasets

1. PostgreSQL persistence for signals, patterns, and pipeline runs
2. Redis for low-latency hot paths and session-level state
3. Seed bootstrap data for deterministic startup and resilience

### 6.3 API contract approach

1. Pydantic response models for stable shape
2. Explicit optionality for partially available fields
3. Backward-compatible extensions (citations, highlights, render status)

## 7. Intelligence Pipeline Architecture

### 7.1 Pipeline stages

1. Ingestion
- Pulls feed snapshots and event streams.

2. Feature engineering
- Computes RSI, SMA relationships, volume ratios, anomaly candidates.

3. Scoring and ranking
- Produces confidence-linked ranking and expected horizon profile.

4. Enrichment
- Generates narratives, watch items, and citations.

5. Persistence and distribution
- Writes to DB and cache, serves module APIs.

### 7.2 Operational controls

1. Run status logging in pipeline_runs
2. Health capability flags for DB, Redis, and model providers
3. Graceful fallback paths when feed quality degrades

## 8. Mathematics and Quant Layer

### 8.1 Anomaly normalization

z-score:

z = (x - mu) / sigma

Interpretation:

- larger |z| implies stronger deviation from baseline behavior

### 8.2 Opportunity ranking

Current weighted score:

score = 55 * confidence + 12 * |z| + 25 * win_rate + 0.7 * min(|avg_30d_return| * 100, 12)

Intent:

- balance model confidence, anomaly strength, historical hit-rate, and projected edge

### 8.3 Horizon projection

Confidence-weighted base return:

base = weighted_avg(avg_30d_return, confidence)

Projected horizons:

- T+1 = 0.22 * base
- T+5 = 0.48 * base
- T+30 = 1.00 * base

### 8.4 Calibration analytics

Confidence is bucketed and compared to realized historical win-rate proxy.

gap = realized - predicted

Monitoring metric:

- mean absolute error across non-empty buckets

## 9. AI System Design

### 9.1 Model routing

1. Mistral as primary structured generation engine
2. Gemini as fallback path

### 9.2 Prompt strategy

1. Module-specific prompt templates
2. Strict JSON output schema
3. Context windows assembled from live signals and patterns

### 9.3 Hallucination control

1. Numeric context injected from deterministic services
2. Citation and source requirements in response shape
3. Service-level fallback responses when model path fails

## 10. UX and Trust Architecture

### 10.1 State visibility

1. Live status strip for system capabilities
2. Route-level transition loading with explicit hints
3. Video render status progression in story module

### 10.2 Trust surfaces

1. Evidence chips on radar cards
2. Chat confidence and highlight chips
3. Clickable citations and audit route links
4. Calibration panel for confidence quality transparency

### 10.3 Decision readiness

1. Ranked opportunities
2. Watch items and tactical hints
3. Portfolio-specific Q and A responses

## 11. Current Build Scope

Implemented now:

1. Opportunity radar ranking and evidence links
2. Signal performance tracker (T+1, T+5, T+30)
3. Confidence calibration buckets and MAE
4. Source-cited chat with citations and confidence
5. Portfolio upload analysis and ask-your-portfolio flow
6. Story arcs and video queue simulation lifecycle
7. Health and capability telemetry

## 12. Risk Register

### 12.1 Technical risks

1. Upstream endpoint volatility
2. Symbol alias and mapping drift
3. Runtime chunk/cache corruption in long-running dev sessions

### 12.2 Product risks

1. Over-reliance on projected metrics without enough realized attribution
2. Variability in feed quality can reduce response consistency

### 12.3 Mitigations

1. startup health checks and deterministic build resets
2. feed retry and fallback paths
3. strict output contracts and schema-first responses

## 13. Productionization Plan

### Phase 1: Reliability hardening

1. One-command startup checks for backend and frontend
2. standardized process lifecycle and cache cleanup scripts
3. feed quality checks and anomaly alerts

### Phase 2: Quant credibility

1. realized return ledger with timestamped outcomes
2. calibration drift alarms
3. confidence-aware retraining and threshold tuning

### Phase 3: Scale and operations

1. queue-backed worker decomposition
2. independent service scaling for API and pipeline
3. expanded observability dashboards

## 14. Why MarketNerve Can Win

Most products in this category stop at either dashboards or generic AI chat.
MarketNerve combines:

1. Statistical ranking
2. Explainable AI outputs
3. Portfolio-native intelligence
4. Evidence and auditability
5. Operational visibility

That integration is the strategic moat and the reason this architecture is designed as an intelligence system, not a feature collection.