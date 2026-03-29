"""
Chat route — AI Market ChatGPT endpoint.
POST /api/chat — answers market questions using Gemini + context from signals/patterns.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat import answer_market_question

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    context: dict | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
    highlights: list[str] = []
    confidence: float | None = None
    citations: list[dict[str, str]] = []
    disclaimer: str = "AI-generated intelligence. Not financial advice."


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = await answer_market_question(req.question, req.context or {})
    return ChatResponse(**result)
