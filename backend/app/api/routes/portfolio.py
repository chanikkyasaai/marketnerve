from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.portfolio import analyze_portfolio, answer_question

router = APIRouter()


class PortfolioRequest(BaseModel):
    csv_text: Optional[str] = None
    use_demo_data: bool = False


class QueryRequest(BaseModel):
    question: str
    csv_text: Optional[str] = None
    use_demo_data: bool = False


@router.post("/portfolio/analyze")
async def analyze(req: PortfolioRequest):
    return await analyze_portfolio(
        csv_text=req.csv_text or "",
        use_demo_data=req.use_demo_data,
    )


@router.post("/portfolio/query")
async def query(req: QueryRequest):
    # Get portfolio data first, then ask Gemini
    portfolio = await analyze_portfolio(
        csv_text=req.csv_text or "",
        use_demo_data=req.use_demo_data,
    )
    result = await answer_question(req.question, portfolio)
    return result
