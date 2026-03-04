"""
Chatbot Router
==============
Handles AI career guidance chatbot conversations.
Supports session-based conversation history.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from backend.utils.dependencies import get_current_user_optional
from backend import models
from backend.services.chatbot_service import get_ai_response

router = APIRouter()

# In-memory conversation store (production should use Redis or DB)
conversation_sessions: Dict[str, List[Dict]] = {}


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"


@router.post("/chat")
async def chat(
    body: ChatMessage,
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """Send a message to the AI career chatbot."""
    session_key = f"{current_user.id if current_user else 'anon'}_{body.session_id}"

    # Get conversation history
    history = conversation_sessions.get(session_key, [])

    # Get AI response
    response = await get_ai_response(body.message, history)

    # Update history
    history.append({"role": "user", "content": body.message})
    history.append({"role": "assistant", "content": response["reply"]})
    conversation_sessions[session_key] = history[-10:]  # Keep last 10 messages

    return {
        "reply": response["reply"],
        "sources": response.get("sources", []),
        "provider": response.get("provider", "rule-based"),
        "session_id": body.session_id
    }


@router.delete("/chat/history")
def clear_chat_history(
    session_id: str = "default",
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """Clear conversation history for a session."""
    session_key = f"{current_user.id if current_user else 'anon'}_{session_id}"
    conversation_sessions.pop(session_key, None)
    return {"message": "Chat history cleared"}
