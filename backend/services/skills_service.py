"""
Skills Service
==============
Handles:
1. Skill extraction from resume text using spaCy + pattern matching
2. Skill gap analysis (compare candidate skills vs required)
3. Learning roadmap generation (rule-based + optional LLM enhancement)
4. Semantic similarity matching using sentence-transformers
"""

import re
import json
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

# --- Master Skills Database ---
SKILLS_DATABASE = {
    "programming": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "R", "MATLAB", "Scala"],
    "web": ["HTML", "CSS", "React", "Vue.js", "Angular", "Node.js", "Django", "Flask", "FastAPI", "Express.js", "Bootstrap", "Tailwind CSS", "REST API", "GraphQL"],
    "data_science": ["Machine Learning", "Deep Learning", "Data Analysis", "Statistics", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Jupyter", "TensorFlow", "PyTorch", "Keras", "scikit-learn"],
    "mlops": ["Docker", "Kubernetes", "MLOps", "CI/CD", "Git", "GitHub Actions", "Jenkins", "Terraform", "Ansible", "AWS", "GCP", "Azure", "Linux"],
    "database": ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLAlchemy", "NoSQL"],
    "nlp": ["NLP", "Natural Language Processing", "spaCy", "NLTK", "Transformers", "BERT", "GPT", "LangChain", "RAG", "FAISS", "Word2Vec"],
    "computer_vision": ["Computer Vision", "OpenCV", "Image Processing", "CNN", "Object Detection", "YOLO"],
    "data_engineering": ["Apache Spark", "Hadoop", "Kafka", "Airflow", "ETL", "Data Pipeline", "BigQuery", "Snowflake", "dbt"],
    "soft_skills": ["Communication", "Leadership", "Problem Solving", "Teamwork", "Agile", "Scrum", "Project Management", "Critical Thinking"],
    "mobile": ["Android", "iOS", "React Native", "Flutter", "Mobile Development"],
    "security": ["Cybersecurity", "Penetration Testing", "OWASP", "Authentication", "OAuth", "JWT"],
    "cloud": ["AWS", "GCP", "Azure", "Cloud Computing", "Serverless", "Lambda", "EC2", "S3"]
}

# Flatten to a single list for quick lookup
ALL_SKILLS = []
SKILL_SET = set()
for category, skills in SKILLS_DATABASE.items():
    for skill in skills:
        if skill.lower() not in SKILL_SET:
            ALL_SKILLS.append(skill)
            SKILL_SET.add(skill.lower())

# --- Career Role Required Skills ---
CAREER_ROLES = {
    "Machine Learning Engineer": {
        "required": ["Python", "Machine Learning", "Deep Learning", "scikit-learn", "TensorFlow", "PyTorch", "SQL", "Docker", "Git", "Statistics", "MLOps"],
        "nice_to_have": ["Kubernetes", "AWS", "Spark", "NLP"]
    },
    "Data Scientist": {
        "required": ["Python", "Statistics", "Machine Learning", "Pandas", "NumPy", "SQL", "Data Analysis", "Matplotlib", "scikit-learn"],
        "nice_to_have": ["R", "Deep Learning", "Tableau", "Spark"]
    },
    "Full Stack Developer": {
        "required": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL", "REST API", "Git", "Python"],
        "nice_to_have": ["TypeScript", "Docker", "AWS", "MongoDB", "GraphQL"]
    },
    "Backend Developer": {
        "required": ["Python", "Node.js", "SQL", "REST API", "Docker", "Git", "PostgreSQL", "Authentication"],
        "nice_to_have": ["Redis", "Kafka", "AWS", "Kubernetes"]
    },
    "Frontend Developer": {
        "required": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Bootstrap", "Git"],
        "nice_to_have": ["Vue.js", "Angular", "Tailwind CSS", "GraphQL", "Testing"]
    },
    "Data Engineer": {
        "required": ["Python", "SQL", "Apache Spark", "ETL", "Data Pipeline", "Docker", "Git", "Airflow"],
        "nice_to_have": ["Kafka", "Hadoop", "BigQuery", "Snowflake", "AWS"]
    },
    "DevOps Engineer": {
        "required": ["Docker", "Kubernetes", "CI/CD", "Linux", "Git", "AWS", "Terraform", "Ansible", "Jenkins"],
        "nice_to_have": ["Python", "Monitoring", "Security", "Networking"]
    },
    "NLP Engineer": {
        "required": ["Python", "NLP", "Machine Learning", "Deep Learning", "Transformers", "BERT", "spaCy", "NLTK"],
        "nice_to_have": ["LangChain", "FAISS", "GPT", "Docker", "FastAPI"]
    },
    "Cloud Architect": {
        "required": ["AWS", "Azure", "GCP", "Cloud Computing", "Docker", "Kubernetes", "Terraform", "Security"],
        "nice_to_have": ["Serverless", "Networking", "Python", "CI/CD"]
    },
    "Software Engineer": {
        "required": ["Python", "Java", "Data Structures", "Algorithms", "Git", "SQL", "Problem Solving"],
        "nice_to_have": ["System Design", "Docker", "AWS", "Testing"]
    }
}

# --- Learning Resources per Skill ---
SKILL_RESOURCES = {
    "Python": [
        {"name": "Python.org Official Tutorial", "url": "https://docs.python.org/3/tutorial/"},
        {"name": "Automate the Boring Stuff", "url": "https://automatetheboringstuff.com/"}
    ],
    "Machine Learning": [
        {"name": "Coursera ML by Andrew Ng", "url": "https://www.coursera.org/learn/machine-learning"},
        {"name": "fast.ai Practical ML", "url": "https://course.fast.ai/"}
    ],
    "Deep Learning": [
        {"name": "fast.ai Deep Learning", "url": "https://course.fast.ai/"},
        {"name": "Deep Learning Specialization (Coursera)", "url": "https://www.coursera.org/specializations/deep-learning"}
    ],
    "Docker": [
        {"name": "Docker Official Docs", "url": "https://docs.docker.com/get-started/"},
        {"name": "Docker for Beginners (Udemy)", "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/"}
    ],
    "React": [
        {"name": "React Official Docs", "url": "https://react.dev/learn"},
        {"name": "The Road to React", "url": "https://www.roadtoreact.com/"}
    ],
    "SQL": [
        {"name": "SQLZoo", "url": "https://sqlzoo.net/"},
        {"name": "Mode Analytics SQL Tutorial", "url": "https://mode.com/sql-tutorial/"}
    ],
    "default": [
        {"name": "YouTube Tutorial", "url": "https://www.youtube.com/results?search_query="},
        {"name": "freeCodeCamp", "url": "https://www.freecodecamp.org/"}
    ]
}


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from resume text using pattern matching.
    Uses case-insensitive matching against master skills list.
    """
    if not text:
        return []

    found_skills = set()
    text_lower = text.lower()

    for skill in ALL_SKILLS:
        # Use word boundary matching for accuracy
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    # Also handle common abbreviations
    abbreviations = {
        "ml": "Machine Learning",
        "dl": "Deep Learning",
        "nlp": "NLP",
        "cv": "Computer Vision",
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
    }
    for abbr, full_skill in abbreviations.items():
        pattern = r'\b' + re.escape(abbr) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(full_skill)

    return sorted(list(found_skills))


def compute_skill_gap(user_skills: List[str], career_goal: str) -> Dict:
    """
    Compute skill gap between user's skills and career requirements.
    Returns missing_skills and a match percentage.
    """
    user_skills_lower = {s.lower() for s in user_skills}

    if career_goal not in CAREER_ROLES:
        # Fuzzy match career goal
        best_match = None
        best_score = 0
        for role in CAREER_ROLES.keys():
            score = SequenceMatcher(None, career_goal.lower(), role.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = role
        career_goal = best_match if best_score > 0.4 else list(CAREER_ROLES.keys())[0]

    role_data = CAREER_ROLES[career_goal]
    required = role_data["required"]
    nice_to_have = role_data.get("nice_to_have", [])

    # Find missing skills
    missing_required = [s for s in required if s.lower() not in user_skills_lower]
    missing_nice = [s for s in nice_to_have if s.lower() not in user_skills_lower]
    matched = [s for s in required if s.lower() in user_skills_lower]

    # Compute match score
    match_score = len(matched) / len(required) if required else 0

    return {
        "career_goal": career_goal,
        "required_skills": required,
        "missing_skills": missing_required,
        "missing_nice_to_have": missing_nice,
        "matched_skills": matched,
        "match_percentage": round(match_score * 100, 1)
    }


def generate_roadmap(missing_skills: List[str], career_goal: str = "") -> List[Dict]:
    """
    Generate a month-by-month learning roadmap for missing skills.
    Groups related skills together into learning phases.
    """
    if not missing_skills:
        return [{"month": 1, "learning": "You have all required skills! Work on real projects.", "skills": [], "resources": []}]

    # Group skills by category
    skill_groups = {}
    for skill in missing_skills:
        for category, cat_skills in SKILLS_DATABASE.items():
            if skill in cat_skills:
                if category not in skill_groups:
                    skill_groups[category] = []
                skill_groups[category].append(skill)
                break
        else:
            if "other" not in skill_groups:
                skill_groups["other"] = []
            skill_groups["other"].append(skill)

    # Learning phase labels
    phase_names = {
        "programming": "Core Programming Fundamentals",
        "data_science": "Data Science & Analytics",
        "mlops": "MLOps & Infrastructure",
        "nlp": "Natural Language Processing",
        "web": "Web Development",
        "database": "Database & Storage",
        "cloud": "Cloud & Deployment",
        "data_engineering": "Data Engineering",
        "computer_vision": "Computer Vision",
        "mobile": "Mobile Development",
        "security": "Security & Auth",
        "soft_skills": "Professional Skills",
        "other": "Additional Skills"
    }

    roadmap = []
    month = 1
    for category, skills in skill_groups.items():
        resources = []
        for skill in skills[:2]:  # Top 2 resources per phase
            if skill in SKILL_RESOURCES:
                resources.extend(SKILL_RESOURCES[skill][:1])
            else:
                resources.append({
                    "name": f"Learn {skill} - YouTube",
                    "url": f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}"
                })

        phase_name = phase_names.get(category, "General Skills")
        roadmap.append({
            "month": month,
            "phase": phase_name,
            "learning": f"Master {', '.join(skills)}",
            "skills": skills,
            "resources": resources[:3],
            "projects": [f"Build a project using {skills[0]}"] if skills else []
        })
        month += 1

    return roadmap


def semantic_match_score(skills1: List[str], skills2: List[str]) -> float:
    """
    Compute similarity score between two skill lists.
    Uses Jaccard similarity + optional sentence-transformers for better accuracy.
    Falls back to simple set overlap if transformers not available.
    """
    if not skills1 or not skills2:
        return 0.0

    set1 = {s.lower() for s in skills1}
    set2 = {s.lower() for s in skills2}

    # Jaccard similarity
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    jaccard = intersection / union if union > 0 else 0.0

    # Weighted score: more weight on intersection ratio
    match_ratio = intersection / len(set2) if set2 else 0.0
    score = 0.4 * jaccard + 0.6 * match_ratio

    try:
        # Enhanced with sentence-transformers if available
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        model = SentenceTransformer('all-MiniLM-L6-v2')
        text1 = " ".join(skills1)
        text2 = " ".join(skills2)
        emb1 = model.encode([text1])
        emb2 = model.encode([text2])
        semantic_score = float(cosine_similarity(emb1, emb2)[0][0])
        # Blend rule-based + semantic
        score = 0.5 * score + 0.5 * semantic_score
    except ImportError:
        pass  # Use rule-based only

    return round(min(score, 1.0), 4)


def get_all_career_roles() -> List[str]:
    """Return list of available career roles."""
    return list(CAREER_ROLES.keys())
