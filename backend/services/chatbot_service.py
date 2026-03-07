"""
Chatbot Service - uses new google-genai SDK
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are CareerAI, an expert career counselor and tech mentor.
Help students understand what skills they need, create learning plans, prepare for interviews,
and navigate the tech job market. Be concise, practical, and encouraging.
Always provide specific resources or next steps. Keep responses under 200 words."""

CAREER_QA = {
    "mlops": {
        "reply": "To learn MLOps: 1) Docker basics, 2) CI/CD pipelines, 3) MLflow for tracking, 4) Kubernetes for scaling.",
        "sources": ["https://mlops.community/", "https://mlflow.org"]
    },
    "machine learning": {
        "reply": "Start ML with: 1) Python (NumPy, Pandas), 2) Andrew Ng's ML course, 3) Kaggle competitions, 4) End-to-end projects.",
        "sources": ["https://www.coursera.org/learn/machine-learning", "https://www.kaggle.com/learn"]
    },
    "python": {
        "reply": "Python path: 1) Official tutorial, 2) Automate the Boring Stuff, 3) Build projects daily, 4) Contribute to open-source.",
        "sources": ["https://docs.python.org/3/tutorial/", "https://automatetheboringstuff.com/"]
    },
    "resume": {
        "reply": "Resume tips: 1) Use action verbs, 2) Quantify achievements, 3) Keep to 1 page, 4) Tailor for each job, 5) Add GitHub/portfolio.",
        "sources": ["https://github.com/"]
    },
    "default": {
        "reply": "For career guidance: 1) Identify your target role, 2) Build a structured plan, 3) Work on real projects, 4) Network on LinkedIn. What specific area do you need help with?",
        "sources": ["https://roadmap.sh/", "https://www.freecodecamp.org/"]
    }
}


def get_rule_based_response(message: str) -> Dict:
    msg_lower = message.lower()
    for keyword, response in CAREER_QA.items():
        if keyword in msg_lower:
            return response
    return CAREER_QA["default"]


async def get_ai_response(message: str, conversation_history: List[Dict] = None) -> Dict:
    gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    print(f"[ChatbotService] Gemini key found: {bool(gemini_key)}")

    if gemini_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)

            # Build conversation history
            history = []
            if conversation_history:
                for msg in conversation_history[-6:]:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role == "user":
                        history.append(types.Content(role="user", parts=[types.Part(text=content)]))
                    elif role in ("assistant", "model"):
                        history.append(types.Content(role="model", parts=[types.Part(text=content)]))

            chat = client.chats.create(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                history=history
            )

            response = chat.send_message(message)
            print("[ChatbotService] Gemini response received!")
            return {
                "reply": response.text,
                "sources": [],
                "provider": "gemini"
            }
        except Exception as e:
            print(f"[ChatbotService] Gemini error: {e}")

    print("[ChatbotService] Using rule-based fallback")
    result = get_rule_based_response(message)
    result["provider"] = "rule-based"
    return result
