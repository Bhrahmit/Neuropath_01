"""
Chat Router
===========
AI career chatbot endpoint.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional

from backend.services.chatbot import get_chat_response

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant'
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


@router.post("/chat")
async def chat(data: ChatRequest):
    """Send a message and get AI career guidance response."""
    history = [{"role": m.role, "content": m.content} for m in (data.history or [])]
    result = await get_chat_response(data.message, history)
    return {
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "model": result.get("model", "unknown"),
    }
