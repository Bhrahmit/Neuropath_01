"""
SQLAlchemy Models
=================
Defines all database tables: Users, StudentProfiles, Resumes,
Skills, JobRoles, Jobs, CandidateMatches, LearningRoadmaps.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
import enum

from backend.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    recruiter = "recruiter"


class User(Base):
    """User accounts for both students and recruiters."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student")  # 'student' | 'recruiter'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    jobs = relationship("Job", back_populates="recruiter")
    roadmaps = relationship("LearningRoadmap", back_populates="user")


class StudentProfile(Base):
    """Extended profile for student users."""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    career_goal = Column(String(200))
    skills = Column(JSON, default=list)       # ["Python", "SQL", ...]
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="student_profile")
    resume = relationship("Resume", foreign_keys=[resume_id])


class Resume(Base):
    """Uploaded resume files and extracted content."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String(500))
    extracted_text = Column(Text)
    parsed_sections = Column(JSON, default=dict)   # {education, experience, skills, ...}
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class Skill(Base):
    """Master skills catalog."""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100))             # Programming, ML, Cloud, etc.


class JobRole(Base):
    """Predefined career roles with required skills."""
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(200), unique=True, nullable=False)
    required_skills = Column(JSON, default=list)   # ["Python", "TensorFlow", ...]
    description = Column(Text)


class Job(Base):
    """Recruiter-posted job listings."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"))
    job_title = Column(String(200), nullable=False)
    description = Column(Text)
    required_skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    recruiter = relationship("User", back_populates="jobs")
    matches = relationship("CandidateMatch", back_populates="job")


class CandidateMatch(Base):
    """Match scores between candidates and job postings."""
    __tablename__ = "candidate_matches"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    candidate_id = Column(Integer, ForeignKey("users.id"))
    match_score = Column(Float)
    missing_skills = Column(JSON, default=list)
    details = Column(JSON, default=dict)          # matched_phrases, reasons
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="matches")
    candidate = relationship("User")


class LearningRoadmap(Base):
    """Generated learning roadmaps for students."""
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    missing_skills = Column(JSON, default=list)
    roadmap_steps = Column(JSON, default=list)    # [{month, skill, resources, ...}, ...]
    career_goal = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="roadmaps")
