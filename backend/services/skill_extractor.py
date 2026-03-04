"""
Skill Extractor Service
=======================
Extracts skills from resume text using:
1. Pattern matching against master skills list
2. spaCy NER (if available)
3. Fuzzy matching for near-matches
"""

import re
from typing import List, Set

# Try importing spaCy
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False

# Master skills list (extended)
MASTER_SKILLS = [
    # Programming
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    # ML/AI
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
    "Computer Vision", "TensorFlow", "PyTorch", "Keras", "scikit-learn",
    "Hugging Face", "LangChain", "MLOps", "XGBoost", "LightGBM",
    "Reinforcement Learning", "Generative AI", "LLM", "BERT", "GPT",
    "FAISS", "RAG", "Vector Database",
    # Data
    "Pandas", "NumPy", "Data Analysis", "Data Science", "Statistics",
    "SQL", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis",
    "Apache Spark", "Hadoop", "ETL", "Data Engineering", "Data Warehouse",
    "Tableau", "Power BI", "Matplotlib", "Seaborn", "Plotly",
    "Linear Algebra", "Probability",
    # Web
    "React", "Angular", "Vue.js", "Node.js", "FastAPI", "Django", "Flask",
    "REST APIs", "GraphQL", "HTML", "CSS", "HTML/CSS", "Bootstrap",
    "Tailwind CSS", "Next.js", "Express.js",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "CI/CD", "Jenkins", "GitHub Actions", "Terraform", "Ansible",
    "Linux", "Git", "GitHub", "GitLab",
    # Other
    "System Design", "Microservices", "Agile", "Scrum", "JIRA",
    "Data Structures", "Algorithms", "OOP", "Design Patterns",
    "Selenium", "Pytest", "Unit Testing",
]

# Build lookup sets for faster matching
SKILLS_LOWER = {s.lower(): s for s in MASTER_SKILLS}
SKILLS_SET = set(MASTER_SKILLS)


def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from resume text using pattern matching + optional spaCy."""
    found_skills: Set[str] = set()
    text_lower = text.lower()
    
    # 1. Direct pattern matching
    for skill_lower, skill_canonical in SKILLS_LOWER.items():
        # Match whole word/phrase
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill_canonical)
    
    # 2. spaCy NER for additional entities (tech-related nouns)
    if SPACY_AVAILABLE:
        try:
            doc = nlp(text[:5000])  # Limit to 5k chars for speed
            for ent in doc.ents:
                ent_text = ent.text.strip()
                if ent_text.lower() in SKILLS_LOWER:
                    found_skills.add(SKILLS_LOWER[ent_text.lower()])
        except Exception:
            pass
    
    # 3. Common abbreviations and aliases
    aliases = {
        "ml": "Machine Learning",
        "dl": "Deep Learning",
        "ai": "Machine Learning",
        "nlp": "NLP",
        "cv": "Computer Vision",
        "tf": "TensorFlow",
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "k8s": "Kubernetes",
    }
    for alias, canonical in aliases.items():
        if re.search(r'\b' + alias + r'\b', text_lower):
            found_skills.add(canonical)
    
    return sorted(list(found_skills))


def compute_skill_gap(user_skills: List[str], required_skills: List[str]) -> List[str]:
    """Find skills in required_skills that user doesn't have."""
    user_lower = {s.lower() for s in user_skills}
    missing = []
    for skill in required_skills:
        if skill.lower() not in user_lower:
            missing.append(skill)
    return missing
