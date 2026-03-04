"""
Skills Router
=============
Endpoints for skill gap analysis and learning roadmap generation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend.database import get_db
from backend.models import User, StudentProfile, JobRole, LearningRoadmap
from backend.utils.dependencies import get_current_user
from backend.services.skill_extractor import compute_skill_gap, MASTER_SKILLS
from backend.services.roadmap_generator import generate_roadmap

router = APIRouter()


class SkillGapRequest(BaseModel):
    career_goal: str
    skills: List[str]


class RoadmapRequest(BaseModel):
    missing_skills: List[str]
    career_goal: Optional[str] = ""
    use_ai: Optional[bool] = False


@router.post("/skill-gap")
async def skill_gap(data: SkillGapRequest, db: Session = Depends(get_db)):
    """Compute missing skills for a career goal."""
    # Find job role in DB
    role = db.query(JobRole).filter(
        JobRole.role_name.ilike(f"%{data.career_goal}%")
    ).first()
    
    if role:
        required = role.required_skills
    else:
        # Fallback: use basic required skills
        required = ["Python", "Machine Learning", "SQL", "Git", "Docker"]
    
    missing = compute_skill_gap(data.skills, required)
    matched = [s for s in required if s not in missing]
    
    return {
        "career_goal": data.career_goal,
        "your_skills": data.skills,
        "required_skills": required,
        "missing_skills": missing,
        "matched_skills": matched,
        "match_percentage": round((len(required) - len(missing)) / len(required) * 100 if required else 0, 1),
    }


@router.post("/generate-roadmap")
def generate_learning_roadmap(
    data: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate personalized learning roadmap for missing skills."""
    roadmap_steps = generate_roadmap(data.missing_skills, data.career_goal)
    
    # Save to DB
    roadmap = LearningRoadmap(
        user_id=current_user.id,
        missing_skills=data.missing_skills,
        roadmap_steps=roadmap_steps,
        career_goal=data.career_goal,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    
    return {
        "roadmap_id": roadmap.id,
        "career_goal": data.career_goal,
        "total_months": len(roadmap_steps),
        "roadmap": roadmap_steps,
    }


@router.get("/skills/list")
def list_skills():
    """Get master list of all skills."""
    return {"skills": sorted(MASTER_SKILLS)}


@router.get("/job-roles")
def list_job_roles(db: Session = Depends(get_db)):
    """Get all predefined career roles."""
    roles = db.query(JobRole).all()
    return {
        "roles": [
            {
                "id": r.id,
                "role_name": r.role_name,
                "required_skills": r.required_skills,
                "description": r.description,
            }
            for r in roles
        ]
    }


@router.get("/roadmaps/my")
def get_my_roadmaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roadmaps for the current user."""
    roadmaps = db.query(LearningRoadmap).filter_by(user_id=current_user.id).all()
    return {
        "roadmaps": [
            {
                "id": r.id,
                "career_goal": r.career_goal,
                "total_months": len(r.roadmap_steps),
                "created_at": r.created_at.isoformat(),
                "roadmap": r.roadmap_steps,
            }
            for r in roadmaps
        ]
    }
