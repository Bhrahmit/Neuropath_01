"""
Seed Data
=========
Populates the database with initial job roles and skills on first run.
Called from main.py lifespan on startup.
"""

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import JobRole, Skill


INITIAL_JOB_ROLES = [
    {
        "role_name": "Machine Learning Engineer",
        "description": "Design, build and deploy machine learning models and pipelines.",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "scikit-learn",
                            "TensorFlow", "PyTorch", "SQL", "Docker", "Git", "Statistics", "MLOps"],
    },
    {
        "role_name": "Data Scientist",
        "description": "Analyze complex data and build predictive models to drive decisions.",
        "required_skills": ["Python", "Statistics", "Machine Learning", "Pandas", "NumPy",
                            "SQL", "Data Analysis", "Matplotlib", "scikit-learn"],
    },
    {
        "role_name": "Full Stack Developer",
        "description": "Build end-to-end web applications across frontend and backend.",
        "required_skills": ["JavaScript", "React", "Node.js", "HTML/CSS", "SQL",
                            "REST APIs", "Git", "Python", "Docker"],
    },
    {
        "role_name": "Backend Developer",
        "description": "Build server-side logic, APIs, and databases.",
        "required_skills": ["Python", "Node.js", "SQL", "REST APIs", "Docker",
                            "Git", "PostgreSQL"],
    },
    {
        "role_name": "Frontend Developer",
        "description": "Build responsive, user-friendly web interfaces.",
        "required_skills": ["JavaScript", "React", "HTML/CSS", "TypeScript",
                            "Bootstrap", "Git"],
    },
    {
        "role_name": "Data Engineer",
        "description": "Build data pipelines and infrastructure for analytics.",
        "required_skills": ["Python", "SQL", "Apache Spark", "ETL", "Docker",
                            "Git", "Airflow"],
    },
    {
        "role_name": "DevOps Engineer",
        "description": "Automate deployment, monitoring, and infrastructure management.",
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "Linux", "Git",
                            "AWS", "Terraform", "Jenkins"],
    },
    {
        "role_name": "NLP Engineer",
        "description": "Build natural language processing models and applications.",
        "required_skills": ["Python", "NLP", "Machine Learning", "Deep Learning",
                            "TensorFlow", "PyTorch"],
    },
    {
        "role_name": "Software Engineer",
        "description": "Design, develop, and maintain software systems.",
        "required_skills": ["Python", "Data Structures", "Algorithms", "Git",
                            "SQL", "OOP"],
    },
    {
        "role_name": "Cloud Architect",
        "description": "Design and manage cloud infrastructure and services.",
        "required_skills": ["AWS", "Azure", "Docker", "Kubernetes",
                            "Terraform", "Linux", "CI/CD"],
    },
]

INITIAL_SKILLS = [
    ("Python", "Programming"), ("JavaScript", "Programming"), ("TypeScript", "Programming"),
    ("Java", "Programming"), ("C++", "Programming"), ("Go", "Programming"),
    ("Machine Learning", "AI/ML"), ("Deep Learning", "AI/ML"), ("NLP", "AI/ML"),
    ("TensorFlow", "AI/ML"), ("PyTorch", "AI/ML"), ("scikit-learn", "AI/ML"),
    ("MLOps", "AI/ML"), ("Computer Vision", "AI/ML"),
    ("SQL", "Data"), ("PostgreSQL", "Data"), ("MySQL", "Data"), ("MongoDB", "Data"),
    ("Pandas", "Data"), ("NumPy", "Data"), ("Data Analysis", "Data"),
    ("React", "Web"), ("Node.js", "Web"), ("HTML/CSS", "Web"), ("FastAPI", "Web"),
    ("Django", "Web"), ("Flask", "Web"), ("REST APIs", "Web"),
    ("Docker", "DevOps"), ("Kubernetes", "DevOps"), ("CI/CD", "DevOps"),
    ("AWS", "Cloud"), ("Azure", "Cloud"), ("GCP", "Cloud"),
    ("Git", "Tools"), ("Linux", "Tools"), ("Statistics", "Mathematics"),
    ("Data Structures", "CS Fundamentals"), ("Algorithms", "CS Fundamentals"),
]


def seed_database():
    """Seed initial data if tables are empty."""
    db: Session = SessionLocal()
    try:
        # Seed job roles
        if db.query(JobRole).count() == 0:
            for role_data in INITIAL_JOB_ROLES:
                role = JobRole(**role_data)
                db.add(role)
            db.commit()
            print(f"[Seed] Added {len(INITIAL_JOB_ROLES)} job roles.")

        # Seed skills
        if db.query(Skill).count() == 0:
            for skill_name, category in INITIAL_SKILLS:
                skill = Skill(name=skill_name, category=category)
                db.add(skill)
            db.commit()
            print(f"[Seed] Added {len(INITIAL_SKILLS)} skills.")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Warning: {e}")
    finally:
        db.close()
