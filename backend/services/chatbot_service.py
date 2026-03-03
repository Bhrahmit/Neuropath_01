"""
Chatbot Service
===============
Provides AI-powered career guidance chatbot using:
- Google Gemini API (primary)
- OpenAI API (fallback)
- Rule-based responses (offline fallback)

Supports conversational memory and career-specific context.
"""

import os
import re
from typing import List, Dict, Optional

# --- Predefined Career Q&A (Rule-based fallback) ---
CAREER_QA = {
    "mlops": {
        "reply": "To learn MLOps, start with: 1) Docker basics (containerize ML models), 2) Git & CI/CD pipelines (GitHub Actions), 3) Model deployment with FastAPI/Flask, 4) Monitoring with MLflow or Weights & Biases, 5) Kubernetes for scaling. Hands-on projects are key!",
        "sources": ["https://mlops.community/", "https://www.mlflow.org/docs/latest/index.html"]
    },
    "machine learning": {
        "reply": "Start your ML journey with: 1) Python fundamentals (NumPy, Pandas), 2) Statistics & Linear Algebra basics, 3) Andrew Ng's ML course on Coursera, 4) Practice with Kaggle competitions, 5) Build end-to-end projects. The key is consistent daily practice!",
        "sources": ["https://www.coursera.org/learn/machine-learning", "https://www.kaggle.com/learn"]
    },
    "deep learning": {
        "reply": "For Deep Learning: 1) Understand neural network basics, 2) Learn PyTorch or TensorFlow, 3) fast.ai practical course is excellent, 4) Study CNNs for vision, RNNs/Transformers for NLP, 5) Implement papers from scratch. GPU access via Google Colab is free!",
        "sources": ["https://course.fast.ai/", "https://pytorch.org/tutorials/"]
    },
    "python": {
        "reply": "Python learning path: 1) Official Python tutorial (python.org), 2) 'Automate the Boring Stuff' (free online), 3) Build small projects daily, 4) Learn OOP and design patterns, 5) Contribute to open-source. Aim for 30 mins of coding every day!",
        "sources": ["https://docs.python.org/3/tutorial/", "https://automatetheboringstuff.com/"]
    },
    "docker": {
        "reply": "Docker essentials: 1) Understand containers vs VMs, 2) Learn Dockerfile syntax, 3) Build and run images, 4) Docker Compose for multi-service apps, 5) Push to Docker Hub. Official docs + 'Docker for Beginners' on YouTube are great starting points!",
        "sources": ["https://docs.docker.com/get-started/", "https://www.youtube.com/results?search_query=docker+tutorial"]
    },
    "react": {
        "reply": "React learning path: 1) Solid JavaScript ES6+ knowledge first, 2) Official React docs (react.dev) are excellent, 3) Learn hooks (useState, useEffect), 4) State management with Context or Redux, 5) Build 3-4 real projects. React is very in-demand!",
        "sources": ["https://react.dev/learn", "https://javascript.info/"]
    },
    "job interview": {
        "reply": "Interview prep strategy: 1) LeetCode for DSA (focus on Easy/Medium first), 2) System Design (Grokking System Design), 3) Behavioral questions (STAR method), 4) Research the company thoroughly, 5) Mock interviews with friends or pramp.com. Consistency beats cramming!",
        "sources": ["https://leetcode.com/", "https://www.pramp.com/"]
    },
    "sql": {
        "reply": "SQL mastery roadmap: 1) Basic queries (SELECT, WHERE, GROUP BY), 2) JOINs (inner, left, right), 3) Window functions, 4) Query optimization and indexes, 5) Practice on SQLZoo and Mode Analytics. SQL is used everywhere - definitely worth mastering!",
        "sources": ["https://sqlzoo.net/", "https://mode.com/sql-tutorial/"]
    },
    "resume": {
        "reply": "Resume tips: 1) Use strong action verbs (Developed, Built, Improved), 2) Quantify achievements (Increased performance by 40%), 3) Keep it 1 page for <5 years experience, 4) Tailor for each job posting, 5) Include GitHub/portfolio links. ATS-friendly formatting matters!",
        "sources": ["https://www.levels.fyi/", "https://github.com/"]
    },
    "default": {
        "reply": "Great question! For career guidance in tech, I recommend: 1) Identify your target role and required skills, 2) Build a structured learning plan, 3) Work on real projects and contribute to open source, 4) Network on LinkedIn, 5) Apply consistently. What specific skill or area would you like guidance on?",
        "sources": ["https://roadmap.sh/", "https://www.freecodecamp.org/"]
    }
}


def get_rule_based_response(message: str) -> Dict:
    """Return a predefined response based on keyword matching."""
    message_lower = message.lower()
    for keyword, response in CAREER_QA.items():
        if keyword in message_lower:
            return response
    return CAREER_QA["default"]


async def get_ai_response(message: str, conversation_history: List[Dict] = None) -> Dict:
    """
    Get AI response from Gemini (primary) or OpenAI (fallback).
    Falls back to rule-based if no API keys configured.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    system_prompt = """You are CareerAI, an expert career counselor and tech mentor. 
    Your role is to help students:
    1. Understand what skills they need for their target career
    2. Create actionable learning plans
    3. Prepare for job interviews
    4. Navigate the tech job market
    
    Be concise, practical, and encouraging. Always provide specific resources or next steps.
    Keep responses under 200 words unless detail is specifically needed."""

    # Try Gemini first
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')

            # Build conversation context
            history_text = ""
            if conversation_history:
                for msg in conversation_history[-4:]:  # Last 4 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_text += f"{role}: {msg['content']}\n"

            full_prompt = f"{system_prompt}\n\nConversation history:\n{history_text}\nUser: {message}\nAssistant:"
            response = model.generate_content(full_prompt)
            reply_text = response.text

            return {
                "reply": reply_text,
                "sources": [],
                "provider": "gemini"
            }
        except Exception as e:
            pass

    # Try OpenAI
    if OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)

            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history[-6:])
            messages.append({"role": "user", "content": message})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            reply_text = response.choices[0].message.content

            return {
                "reply": reply_text,
                "sources": [],
                "provider": "openai"
            }
        except Exception as e:
            pass

    # Fallback to rule-based
    response = get_rule_based_response(message)
    response["provider"] = "rule-based"
    return response
