"""
Resume Router
=============
Handles resume upload, text extraction, and skill extraction endpoints.
"""

import os
import uuid
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from backend.database import get_db
from backend.models import User, Resume, StudentProfile
from backend.utils.dependencies import get_current_user
from backend.services.resume_parser import extract_text_from_file, parse_sections
from backend.services.skill_extractor import extract_skills_from_text

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and parse a resume file (PDF/DOCX/TXT)."""
    # Validate file type
    allowed = {".pdf", ".docx", ".doc", ".txt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Use PDF, DOCX, or TXT.")
    
    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
    
    # Save file
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    
    # Extract text
    extracted_text = extract_text_from_file(file_bytes, file.filename)
    parsed_sections = parse_sections(extracted_text)
    
    # Save to DB
    resume = Resume(
        user_id=current_user.id,
        file_path=file_path,
        extracted_text=extracted_text,
        parsed_sections=parsed_sections,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    # Auto-extract skills
    skills = extract_skills_from_text(extracted_text)
    
    # Update student profile
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if profile:
        # Merge existing and new skills
        existing = set(profile.skills or [])
        existing.update(skills)
        profile.skills = sorted(list(existing))
        profile.resume_id = resume.id
        db.commit()
    
    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "extracted_skills": skills,
        "word_count": len(extracted_text.split()),
        "sections_found": list(parsed_sections.keys()),
    }


class ExtractSkillsRequest(BaseModel):
    resume_text: str


@router.post("/extract-skills")
def extract_skills(data: ExtractSkillsRequest):
    """Extract skills from raw text (no auth required for quick testing)."""
    skills = extract_skills_from_text(data.resume_text)
    return {"skills": skills, "count": len(skills)}
