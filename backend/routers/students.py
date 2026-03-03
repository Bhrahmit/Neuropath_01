"""
Students Router
===============
Student profile management: update skills, career goal, view profile.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend.database import get_db
from backend.models import User, StudentProfile
from backend.utils.dependencies import get_current_user

router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    career_goal: Optional[str] = None
    skills: Optional[List[str]] = None


@router.get("/student/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student profile with skills and career goal."""
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": profile.id,
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "career_goal": profile.career_goal,
        "skills": profile.skills or [],
    }


@router.put("/student/profile")
def update_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update student career goal and/or skills."""
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id, skills=[])
        db.add(profile)
    
    if data.career_goal is not None:
        profile.career_goal = data.career_goal
    if data.skills is not None:
        profile.skills = data.skills
    
    db.commit()
    return {"message": "Profile updated", "career_goal": profile.career_goal, "skills": profile.skills}
