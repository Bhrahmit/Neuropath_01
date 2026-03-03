"""
CareerAI - Main FastAPI Application
=====================================
Entry point: initializes app, CORS, static files, routers, and page routes.
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from backend.database import engine, Base
from backend.seed_data import seed_database

# Import routers
from backend.routers.auth import router as auth_router
from backend.routers.resume import router as resume_router
from backend.routers.skills import router as skills_router
from backend.routers.jobs import router as jobs_router
from backend.routers.chatbot import router as chatbot_router   # single chat router
from backend.routers.students import router as students_router
from backend.routers.recruiter import router as recruiter_router
from backend.routers.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables and seed data on startup."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="CareerAI API",
    description="AI-powered career guidance and recruitment platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# API Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume_router, prefix="/api", tags=["Resume"])
app.include_router(skills_router, prefix="/api", tags=["Skills"])
app.include_router(jobs_router, prefix="/api", tags=["Jobs"])
app.include_router(chatbot_router, prefix="/api", tags=["Chat"])
app.include_router(students_router, prefix="/api", tags=["Students"])
app.include_router(recruiter_router, prefix="/api", tags=["Recruiter"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])


# ─── HTML Page Routes ──────────────────────────────────────────────────────────

@app.get("/")
async def index():
    return FileResponse("frontend/templates/index.html")

@app.get("/login")
async def login_page():
    return FileResponse("frontend/templates/login.html")

@app.get("/register")
async def register_page():
    return FileResponse("frontend/templates/register.html")

@app.get("/dashboard")
async def dashboard_page():
    return FileResponse("frontend/templates/dashboard.html")

@app.get("/recruiter")
async def recruiter_page():
    return FileResponse("frontend/templates/recruiter.html")

@app.get("/roadmap")
async def roadmap_page():
    return FileResponse("frontend/templates/roadmap.html")

@app.get("/chat")
async def chat_page():
    return FileResponse("frontend/templates/chat.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "CareerAI API v1.0"}
