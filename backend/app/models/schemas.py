from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    name: str
    kind: str = "primary"
    url: str | None = None


class BacktestStats(BaseModel):
    occurrences: int
    wins: int
    losses: int
    win_rate: float
    avg_30d_return: float
    avg_holding_days: int | None = None
    failure_contexts: list[str] = Field(default_factory=list)
    reward_risk_ratio: float | None = None


class Signal(BaseModel):
    id: str
    ticker: str
    company: str
    sector: str
    signal_type: str
    headline: str
    summary: str
    confidence: float
    anomaly_score: float = 0.0
    z_score: float = 0.0
    historical_win_rate: float
    avg_30d_return: float
    impact_score: int
    age_minutes: int
    portfolio_impact_pct: float
    sources: list[str]
    reasoning_steps: list[str]
    watch_items: list[str]


class EnrichedSignal(BaseModel):
    id: str
    ticker: str
    company: str
    sector: str
    signal_type: str
    headline: str
    summary: str
    confidence: float
    anomaly_score: float
    z_score: float
    impact_score: int
    freshness_label: str
    portfolio_impact_pct: float
    sources: list[SourceRef]
    backtest: BacktestStats
    reasoning_chain: list[str]
    watch_items: list[str]
    disclaimer: str
    tags: list[str] = Field(default_factory=list)


class AuditTrail(BaseModel):
    signal_id: str
    ticker: str
    event_timestamp: datetime
    confidence: float
    input_snapshot: dict
    enrichment_snapshot: dict
    reasoning_chain: list[str]
    output: dict
    confidence_metadata: dict
    disclaimer: str


class Pattern(BaseModel):
    id: str = ""
    ticker: str
    company: str
    pattern_type: str
    confidence: float
    occurrences: int
    wins: int
    avg_30d_return: float
    narrative: str
    context: str
    risk_flags: list[str] = Field(default_factory=list)
    reward_risk_ratio: float | None = None


class PatternInsight(BaseModel):
    id: str = ""
    ticker: str
    company: str
    sector: str
    market_cap_band: str
    pattern_type: str
    confidence: float
    signal_strength: str
    backtest: BacktestStats
    narrative: str
    context: str
    risk_flags: list[str] = Field(default_factory=list)


class Holding(BaseModel):
    asset_type: str
    name: str
    symbol: str
    sector: str
    units: float
    invested_amount: float
    current_value: float
    years_held: float = Field(default=1.0)
    lookthrough_exposure: dict[str, float] = Field(default_factory=dict)


class PortfolioUploadRequest(BaseModel):
    csv_text: str | None = None
    use_demo_data: bool = True
    zero_retention_mode: bool = True


class PortfolioQueryRequest(BaseModel):
    question: str
    csv_text: str | None = None
    use_demo_data: bool = True
    zero_retention_mode: bool = True


class ExposureItem(BaseModel):
    name: str
    weight: float
    exposure_type: str


class FundOverlap(BaseModel):
    symbol: str
    overlap_weight: float


class OverlapRow(BaseModel):
    fund: str
    overlaps: list[FundOverlap]


class BenchmarkSnapshot(BaseModel):
    benchmark: str
    benchmark_return: float
    portfolio_return: float
    relative_alpha: float
    commentary: str


class MoneyHealthScore(BaseModel):
    overall: int
    diversification: int
    momentum_alignment: int
    concentration_risk: int
    profit_quality: int
    downside_resilience: int
    liquidity_buffer: int


class PortfolioAnalysisResponse(BaseModel):
    portfolio_name: str
    currency: str
    zero_retention_mode: bool
    holdings_count: int
    invested_amount: float
    current_value: float
    absolute_gain: float
    absolute_return: float
    xirr: float
    direct_equity_weight: float
    mutual_fund_weight: float
    etf_weight: float
    sector_exposure: list[ExposureItem]
    stock_exposure: list[ExposureItem]
    overlap_matrix: list[OverlapRow]
    benchmark_snapshot: BenchmarkSnapshot
    money_health_score: MoneyHealthScore
    risk_flags: list[str]
    recommended_actions: list[str]


class PortfolioAnswer(BaseModel):
    question: str
    answer: str
    logic: list[str]
    sources: list[str]
    supporting_metrics: dict[str, float | int | str]
    disclaimer: str


class StoryVideo(BaseModel):
    title: str
    published_at: str
    duration_seconds: int
    summary: str
    embed_url: str
    mp4_url: str
    formats: list[str]
    lead_signal_id: str | None = None
    script_outline: list[str] = Field(default_factory=list)


class StoryEvent(BaseModel):
    date: str
    label: str
    source: str


class StoryArc(BaseModel):
    slug: str
    title: str
    thesis: str
    sentiment: str
    sentiment_score: float = 0.6
    what_to_watch_next: list[str]
    events: list[StoryEvent]


class IpoInsight(BaseModel):
    name: str
    gmp: int
    subscription_multiple: float
    allotment_probability: float
    demand_label: str
    risk_level: str
    summary: str
    cutoff_price: int | None = None
    listing_date: str | None = None


class HealthResponse(BaseModel):
    status: str
    generated_at: str
    data_freshness_minutes: int
    api_p95_ms: int
    agent_status: dict[str, str]
    pipeline_status: dict[str, str]
    websocket_channels: list[str]
    total_signals_processed: int = 0
    uptime_minutes: int = 0


class SignalSubscriptionRequest(BaseModel):
    watchlist: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    min_confidence: float = 0.0


class SignalSubscriptionResponse(BaseModel):
    subscription_id: str
    stream: str
    filters: dict
    active: bool


class LiveEvent(BaseModel):
    channel: str
    event_type: str
    generated_at: str
    payload: dict


class PaginatedSignalsResponse(BaseModel):
    items: list[EnrichedSignal]
    total: int
    limit: int
    offset: int
    has_more: bool
