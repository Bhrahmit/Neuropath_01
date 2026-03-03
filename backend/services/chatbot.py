"""
AI Career Chatbot Service
==========================
Handles chat with career guidance context.
Uses Gemini API (preferred) or OpenAI API, with rule-based fallback.
"""

import os
from typing import List, Dict

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = """You are CareerAI, an expert career counselor and mentor specializing in tech careers.
You help students navigate their career paths, suggest learning resources, explain technical concepts,
and provide motivational guidance. Be concise, practical, and encouraging.
When suggesting resources, include specific course names, book titles, or website URLs when possible.
Format responses clearly with bullet points when listing items."""

# Rule-based fallback responses
RULE_RESPONSES = {
    "mlops": """To learn MLOps, follow this path:
• **Week 1-2**: Learn Docker basics - containerize your ML models
• **Week 3-4**: Study CI/CD with GitHub Actions or Jenkins
• **Week 5-6**: Explore MLflow for experiment tracking and model registry
• **Week 7-8**: Learn Kubernetes for orchestration

📚 **Resources**:
- MLflow: https://mlflow.org/docs/latest/tutorials-and-examples/
- Coursera MLOps Fundamentals: https://www.coursera.org/learn/mlops-fundamentals
- Full Stack Deep Learning: https://fullstackdeeplearning.com""",
    
    "python": """To learn Python effectively:
• Start with Python for Everybody on Coursera (free audit)
• Practice on LeetCode and HackerRank daily
• Build projects: web scraper, data analyzer, simple ML model

📚 **Resources**:
- https://www.python.org/about/gettingstarted/
- https://www.coursera.org/specializations/python
- Automate the Boring Stuff: https://automatetheboringstuff.com""",
    
    "machine learning": """Machine Learning learning path:
• **Month 1**: Math foundations (Linear Algebra, Statistics, Probability)
• **Month 2**: Andrew Ng's ML Course on Coursera (highly recommended!)
• **Month 3**: Practice with Kaggle competitions
• **Month 4**: Deep Learning fundamentals

📚 **Resources**:
- https://www.coursera.org/learn/machine-learning
- Hands-on ML book: https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/
- Kaggle: https://www.kaggle.com/learn""",
    
    "sql": """Learning SQL:
• Start with SELECT, WHERE, JOIN, GROUP BY basics
• Then learn subqueries, CTEs, window functions
• Practice on LeetCode SQL or Mode Analytics

📚 **Resources**:
- SQLZoo: https://sqlzoo.net
- LeetCode SQL: https://leetcode.com/study-plan/sql/
- Mode SQL Tutorial: https://mode.com/sql-tutorial/""",
}


async def get_chat_response(message: str, history: List[Dict] = None) -> Dict:
    """Get chatbot response. Returns {reply, sources}."""
    
    # Try Gemini first
    if GEMINI_KEY:
        try:
            return await _gemini_response(message, history or [])
        except Exception as e:
            print(f"[Chatbot] Gemini error: {e}")
    
    # Try OpenAI
    if OPENAI_KEY:
        try:
            return await _openai_response(message, history or [])
        except Exception as e:
            print(f"[Chatbot] OpenAI error: {e}")
    
    # Rule-based fallback
    return _rule_based_response(message)


async def _gemini_response(message: str, history: List[Dict]) -> Dict:
    """Get response from Google Gemini API."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_KEY)
    
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    # Build conversation history
    chat = model.start_chat()
    for msg in history[-6:]:  # Last 6 messages for context
        if msg.get("role") == "user":
            chat.send_message(msg["content"])
    
    response = chat.send_message(message)
    return {"reply": response.text, "sources": [], "model": "gemini-1.5-flash"}


async def _openai_response(message: str, history: List[Dict]) -> Dict:
    """Get response from OpenAI API."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_KEY)
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})
    
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
    )
    return {"reply": response.choices[0].message.content, "sources": [], "model": "gpt-3.5-turbo"}


def _rule_based_response(message: str) -> Dict:
    """Fallback rule-based responses for common career questions."""
    msg_lower = message.lower()
    
    for keyword, response in RULE_RESPONSES.items():
        if keyword in msg_lower:
            return {"reply": response, "sources": [], "model": "rule-based"}
    
    # Generic career advice
    return {
        "reply": """Great question! Here's how I'd approach your career development:

1. **Identify your goal**: What role do you want in 1-2 years?
2. **Assess your gaps**: Compare your current skills to job descriptions
3. **Build a roadmap**: Use CareerAI's roadmap feature for a personalized plan
4. **Practice consistently**: 1-2 hours daily beats occasional marathon sessions
5. **Build projects**: Employers value real-world experience

Use the **Skill Gap Analysis** feature above to get your personalized learning plan!

💡 Tip: Try asking me specific questions like "How do I learn Python?" or "What skills do I need for Data Science?" """,
        "sources": [],
        "model": "rule-based"
    }
