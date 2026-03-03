"""
Roadmap Generator Service
==========================
Generates personalized month-by-month learning roadmaps.
Uses rule-based generation with optional LLM enhancement via Gemini/OpenAI.
"""

import os
from typing import List, Dict

# LLM setup (optional)
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")


# ─── Resource database per skill ──────────────────────────────────────────────
SKILL_RESOURCES = {
    "Python": [
        {"type": "course", "title": "Python for Everybody", "url": "https://www.coursera.org/specializations/python"},
        {"type": "docs", "title": "Official Python Docs", "url": "https://docs.python.org/3/"},
        {"type": "book", "title": "Automate the Boring Stuff", "url": "https://automatetheboringstuff.com"},
    ],
    "Machine Learning": [
        {"type": "course", "title": "Andrew Ng ML Course", "url": "https://www.coursera.org/learn/machine-learning"},
        {"type": "book", "title": "Hands-on ML with Scikit-Learn", "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/"},
    ],
    "Deep Learning": [
        {"type": "course", "title": "Deep Learning Specialization", "url": "https://www.coursera.org/specializations/deep-learning"},
        {"type": "docs", "title": "Fast.ai Practical DL", "url": "https://course.fast.ai"},
    ],
    "Docker": [
        {"type": "docs", "title": "Docker Official Docs", "url": "https://docs.docker.com"},
        {"type": "course", "title": "Docker Mastery (Udemy)", "url": "https://www.udemy.com/course/docker-mastery/"},
    ],
    "MLOps": [
        {"type": "course", "title": "MLOps Fundamentals", "url": "https://www.coursera.org/learn/mlops-fundamentals"},
        {"type": "tool", "title": "MLflow Getting Started", "url": "https://mlflow.org/docs/latest/tutorials-and-examples/tutorial.html"},
    ],
    "SQL": [
        {"type": "course", "title": "SQL for Data Science", "url": "https://www.coursera.org/learn/sql-for-data-science"},
        {"type": "practice", "title": "LeetCode SQL Problems", "url": "https://leetcode.com/study-plan/sql/"},
    ],
    "React": [
        {"type": "docs", "title": "React Official Docs", "url": "https://react.dev"},
        {"type": "course", "title": "The Complete React Course", "url": "https://www.udemy.com/course/the-complete-react-fullstack-course/"},
    ],
    "AWS": [
        {"type": "course", "title": "AWS Cloud Practitioner", "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/"},
        {"type": "docs", "title": "AWS Getting Started", "url": "https://aws.amazon.com/getting-started/"},
    ],
    "NLP": [
        {"type": "course", "title": "NLP Specialization (deeplearning.ai)", "url": "https://www.coursera.org/specializations/natural-language-processing"},
        {"type": "docs", "title": "Hugging Face NLP Course", "url": "https://huggingface.co/course"},
    ],
    "Data Analysis": [
        {"type": "course", "title": "Google Data Analytics Certificate", "url": "https://www.coursera.org/professional-certificates/google-data-analytics"},
    ],
}

DEFAULT_RESOURCES = [
    {"type": "search", "title": "Search on YouTube", "url": "https://www.youtube.com/results?search_query="},
    {"type": "search", "title": "Search on Coursera", "url": "https://www.coursera.org/search?query="},
]


def get_skill_difficulty(skill: str) -> str:
    """Estimate difficulty: beginner | intermediate | advanced."""
    advanced = {"Deep Learning", "MLOps", "Kubernetes", "System Design", "Reinforcement Learning", "Computer Vision"}
    beginner = {"Python", "SQL", "HTML/CSS", "Git", "Linux", "Statistics"}
    if skill in advanced:
        return "advanced"
    elif skill in beginner:
        return "beginner"
    return "intermediate"


def get_skill_duration_weeks(skill: str) -> int:
    """Estimate weeks to learn a skill."""
    durations = {
        "Python": 3, "SQL": 2, "Git": 1, "Docker": 2, "HTML/CSS": 2,
        "Machine Learning": 6, "Deep Learning": 8, "MLOps": 4,
        "React": 4, "FastAPI": 2, "AWS": 4, "Kubernetes": 4,
        "NLP": 6, "Computer Vision": 6, "Statistics": 3,
    }
    return durations.get(skill, 3)


def generate_roadmap(missing_skills: List[str], career_goal: str = "") -> List[Dict]:
    """
    Generate a month-by-month learning roadmap for missing skills.
    Skills are ordered by difficulty (beginner first) and grouped into months.
    """
    if not missing_skills:
        return []

    # Sort by difficulty: beginner → intermediate → advanced
    difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    sorted_skills = sorted(
        missing_skills,
        key=lambda s: difficulty_order[get_skill_difficulty(s)]
    )

    roadmap = []
    month = 1
    week_accumulator = 0
    month_skills = []

    for skill in sorted_skills:
        weeks = get_skill_duration_weeks(skill)
        resources = SKILL_RESOURCES.get(skill, [
            {"type": "search", "title": f"Learn {skill} on YouTube",
             "url": f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}"},
            {"type": "search", "title": f"Search {skill} on Coursera",
             "url": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}"},
        ])

        week_accumulator += weeks
        month_skills.append(skill)

        # Group ~4 weeks per month
        if week_accumulator >= 4:
            roadmap.append({
                "month": month,
                "skills": month_skills.copy(),
                "primary_skill": month_skills[0],
                "difficulty": get_skill_difficulty(month_skills[0]),
                "estimated_weeks": week_accumulator,
                "resources": resources,
                "description": f"Focus on {', '.join(month_skills)} to progress toward {career_goal or 'your career goal'}.",
            })
            month += 1
            week_accumulator = 0
            month_skills = []

    # Remaining skills
    if month_skills:
        skill = month_skills[0]
        resources = SKILL_RESOURCES.get(skill, DEFAULT_RESOURCES)
        roadmap.append({
            "month": month,
            "skills": month_skills,
            "primary_skill": skill,
            "difficulty": get_skill_difficulty(skill),
            "estimated_weeks": week_accumulator,
            "resources": resources,
            "description": f"Complete your learning journey with {', '.join(month_skills)}.",
        })

    return roadmap


async def generate_roadmap_with_llm(missing_skills: List[str], career_goal: str) -> List[Dict]:
    """Enhanced roadmap using Gemini API if key is available. Falls back to rule-based."""
    if not GEMINI_KEY:
        return generate_roadmap(missing_skills, career_goal)

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""Create a detailed month-by-month learning roadmap.
Career Goal: {career_goal}
Missing Skills: {', '.join(missing_skills)}

Return JSON array with this format:
[{{"month": 1, "skills": ["Skill1"], "description": "...", "resources": [{{"title":"...", "url":"..."}}]}}]
Only return the JSON array, nothing else."""

        response = model.generate_content(prompt)
        import json, re
        # Extract JSON from response
        text = response.text
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"[LLM] Roadmap generation failed: {e}")

    return generate_roadmap(missing_skills, career_goal)
