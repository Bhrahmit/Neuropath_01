"""
AI Career Chatbot Service - uses new google-genai SDK
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are CareerAI, an expert career counselor and mentor specializing in tech careers.
You help students navigate their career paths, suggest learning resources, explain technical concepts,
and provide motivational guidance. Be concise, practical, and encouraging.
Format responses clearly with bullet points when listing items."""


async def get_chat_response(message: str, history: List[Dict] = None) -> Dict:
    gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    print(f"[Chatbot] Gemini key found: {bool(gemini_key)}")

    if gemini_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)

            # Build proper history
            chat_history = []
            for msg in (history or [])[-6:]:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    chat_history.append(types.Content(role="user", parts=[types.Part(text=content)]))
                elif role in ("assistant", "model"):
                    chat_history.append(types.Content(role="model", parts=[types.Part(text=content)]))

            chat = client.chats.create(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                history=chat_history
            )

            response = chat.send_message(message)
            print("[Chatbot] Gemini response received!")
            return {"reply": response.text, "sources": [], "model": "gemini-2.0-flash-lite"}

        except Exception as e:
            print(f"[Chatbot] Gemini error: {e}")

    print("[Chatbot] Using rule-based fallback")
    return {
        "reply": "I'm here to help with your tech career! Ask me about skills, learning paths, or career advice.",
        "sources": [],
        "model": "rule-based"
    }
