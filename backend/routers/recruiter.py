"""
Recruiter Router
================
Recruiter-specific dashboard data endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, Job, CandidateMatch, StudentProfile
from backend.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/recruiter/stats")
def get_recruiter_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics for recruiter dashboard."""
    total_jobs = db.query(Job).filter_by(recruiter_id=current_user.id).count()
    total_candidates = db.query(StudentProfile).count()
    total_matches = db.query(CandidateMatch).join(Job).filter(
        Job.recruiter_id == current_user.id
    ).count()
    
    avg_score = 0.0
    matches = db.query(CandidateMatch).join(Job).filter(
        Job.recruiter_id == current_user.id
    ).all()
    if matches:
        avg_score = round(sum(m.match_score for m in matches) / len(matches) * 100, 1)
    
    return {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "total_matches": total_matches,
        "avg_match_score": avg_score,
    }
