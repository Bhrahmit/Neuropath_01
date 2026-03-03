"""
Analytics Router
================
Provides statistical data for Chart.js visualizations:
- Skill demand trends
- Match score distributions
- Platform usage statistics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from backend.utils.dependencies import get_current_user
from backend.services.skills_service import SKILLS_DATABASE, CAREER_ROLES

router = APIRouter()


@router.get("/analytics/overview")
def get_overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get platform overview stats."""
    total_students = db.query(models.User).filter(models.User.role == "student").count()
    total_recruiters = db.query(models.User).filter(models.User.role == "recruiter").count()
    total_jobs = db.query(models.Job).count()
    total_matches = db.query(models.CandidateMatch).count()
    total_roadmaps = db.query(models.LearningRoadmap).count()

    return {
        "total_students": total_students,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "total_matches": total_matches,
        "total_roadmaps": total_roadmaps
    }


@router.get("/analytics/top-skills")
def get_top_skills(db: Session = Depends(get_db)):
    """Get the most in-demand skills across all job postings."""
    jobs = db.query(models.Job).all()
    skill_count = {}

    for job in jobs:
        for skill in (job.required_skills or []):
            skill_count[skill] = skill_count.get(skill, 0) + 1

    # Fallback demo data if no jobs
    if not skill_count:
        skill_count = {
            "Python": 45, "Machine Learning": 38, "SQL": 35,
            "Docker": 30, "JavaScript": 28, "React": 25,
            "Deep Learning": 22, "AWS": 20, "Git": 18, "NLP": 15
        }

    sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "labels": [s[0] for s in sorted_skills],
        "data": [s[1] for s in sorted_skills]
    }


@router.get("/analytics/career-distribution")
def get_career_distribution(db: Session = Depends(get_db)):
    """Get distribution of students' career goals."""
    profiles = db.query(models.StudentProfile).all()
    goal_count = {}

    for profile in profiles:
        goal = profile.career_goal or "Not Set"
        goal_count[goal] = goal_count.get(goal, 0) + 1

    # Demo fallback
    if not goal_count or (len(goal_count) == 1 and "Not Set" in goal_count):
        goal_count = {
            "Machine Learning Engineer": 12,
            "Data Scientist": 10,
            "Full Stack Developer": 9,
            "Backend Developer": 7,
            "DevOps Engineer": 5,
            "NLP Engineer": 4,
            "Other": 3
        }

    sorted_goals = sorted(goal_count.items(), key=lambda x: x[1], reverse=True)[:7]
    return {
        "labels": [g[0] for g in sorted_goals],
        "data": [g[1] for g in sorted_goals]
    }


@router.get("/analytics/match-scores")
def get_match_score_distribution(db: Session = Depends(get_db)):
    """Get distribution of candidate match scores."""
    matches = db.query(models.CandidateMatch).all()

    buckets = {"0-20%": 0, "21-40%": 0, "41-60%": 0, "61-80%": 0, "81-100%": 0}
    for match in matches:
        score = (match.match_score or 0) * 100
        if score <= 20: buckets["0-20%"] += 1
        elif score <= 40: buckets["21-40%"] += 1
        elif score <= 60: buckets["41-60%"] += 1
        elif score <= 80: buckets["61-80%"] += 1
        else: buckets["81-100%"] += 1

    return {
        "labels": list(buckets.keys()),
        "data": list(buckets.values())
    }
