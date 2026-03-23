from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import PortfolioQueryRequest, PortfolioUploadRequest
from app.services.portfolio import analyze_portfolio, answer_portfolio_question


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/analyze")
def portfolio_analyze(payload: PortfolioUploadRequest) -> dict:
    return analyze_portfolio(payload.csv_text, payload.use_demo_data, payload.zero_retention_mode).model_dump()


@router.post("/query")
def portfolio_query(payload: PortfolioQueryRequest) -> dict:
    return answer_portfolio_question(
        payload.question,
        payload.csv_text,
        payload.use_demo_data,
        payload.zero_retention_mode,
    ).model_dump()
