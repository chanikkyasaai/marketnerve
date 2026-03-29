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
    result = await analyze_portfolio(
        csv_text=req.csv_text or "",
        use_demo_data=req.use_demo_data,
    )
    return result.model_dump() if hasattr(result, "model_dump") else result


@router.post("/portfolio/query")
async def query(req: QueryRequest):
    try:
        # Get portfolio data first, then ask Gemini
        portfolio = await analyze_portfolio(
            csv_text=req.csv_text or "",
            use_demo_data=req.use_demo_data,
        )
        ans = await answer_question(req.question, portfolio)
        return ans.model_dump() if hasattr(ans, "model_dump") else ans
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
