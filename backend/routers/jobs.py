"""
Jobs Router
===========
Recruiter endpoints: post jobs, match candidates, view results.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend.database import get_db
from backend.models import User, Job, CandidateMatch, StudentProfile
from backend.utils.dependencies import get_current_user
from backend.services.matcher import rank_candidates

router = APIRouter()


class JobPostRequest(BaseModel):
    job_title: str
    description: Optional[str] = ""
    required_skills: List[str]


@router.post("/job-post")
def create_job(
    data: JobPostRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Post a new job listing (recruiter only)."""
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can post jobs")
    
    job = Job(
        recruiter_id=current_user.id,
        job_title=data.job_title,
        description=data.description,
        required_skills=data.required_skills,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return {"job_id": job.id, "message": "Job posted successfully", "job_title": job.job_title}


class MatchCandidatesRequest(BaseModel):
    job_id: int


@router.post("/match-candidates")
def match_candidates(
    data: MatchCandidatesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rank all student candidates for a job posting."""
    job = db.query(Job).filter_by(id=data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your job posting")
    
    # Get all student profiles with skills
    profiles = db.query(StudentProfile).join(User).filter(
        User.role == "student"
    ).all()
    
    candidates = [
        {
            "id": p.user.id,
            "name": p.user.name,
            "email": p.user.email,
            "skills": p.skills or [],
        }
        for p in profiles
        if p.skills
    ]
    
    # Rank candidates
    ranked = rank_candidates(candidates, job.required_skills)
    
    # Save matches to DB
    db.query(CandidateMatch).filter_by(job_id=data.job_id).delete()
    for r in ranked:
        match = CandidateMatch(
            job_id=data.job_id,
            candidate_id=r["id"],
            match_score=r["match_score"],
            missing_skills=r["missing_skills"],
            details={"matched_skills": r["matched_skills"]},
        )
        db.add(match)
    db.commit()
    
    return {
        "job_id": data.job_id,
        "job_title": job.job_title,
        "total_candidates": len(ranked),
        "candidates": ranked,
    }


@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    """List all available jobs (public)."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return {
        "jobs": [
            {
                "id": j.id,
                "job_title": j.job_title,
                "description": j.description,
                "required_skills": j.required_skills,
                "recruiter_name": j.recruiter.name,
                "created_at": j.created_at.isoformat(),
            }
            for j in jobs
        ]
    }


@router.get("/jobs/my")
def my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recruiter's own job postings."""
    jobs = db.query(Job).filter_by(recruiter_id=current_user.id).all()
    return {
        "jobs": [
            {
                "id": j.id,
                "job_title": j.job_title,
                "description": j.description,
                "required_skills": j.required_skills,
                "candidate_count": len(j.matches),
                "created_at": j.created_at.isoformat(),
            }
            for j in jobs
        ]
    }
