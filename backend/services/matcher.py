"""
Candidate Matching Service
===========================
Uses sentence-transformers embeddings + cosine similarity to rank candidates
against job requirements. Falls back to Jaccard similarity if transformers unavailable.
"""

from typing import List, Dict, Tuple
import numpy as np

# Try loading sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False


def _embedding_similarity(skills_a: List[str], skills_b: List[str]) -> float:
    """Compute semantic similarity between two skill lists using embeddings."""
    if not skills_a or not skills_b:
        return 0.0
    
    text_a = ", ".join(skills_a)
    text_b = ", ".join(skills_b)
    
    emb = _model.encode([text_a, text_b])
    # Cosine similarity
    dot = np.dot(emb[0], emb[1])
    norm = np.linalg.norm(emb[0]) * np.linalg.norm(emb[1])
    return float(dot / norm) if norm > 0 else 0.0


def _jaccard_similarity(skills_a: List[str], skills_b: List[str]) -> float:
    """Fallback: Jaccard similarity between skill sets."""
    set_a = {s.lower() for s in skills_a}
    set_b = {s.lower() for s in skills_b}
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def compute_match_score(candidate_skills: List[str], job_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Compute match score, matched skills, and missing skills.
    Returns: (score 0-1, matched_skills, missing_skills)
    """
    candidate_lower = {s.lower(): s for s in candidate_skills}
    job_lower = {s.lower(): s for s in job_skills}
    
    matched = [job_lower[s] for s in job_lower if s in candidate_lower]
    missing = [job_lower[s] for s in job_lower if s not in candidate_lower]
    
    # Base score: matched fraction
    base_score = len(matched) / len(job_skills) if job_skills else 0.0
    
    # Boost with semantic similarity if available
    if TRANSFORMERS_AVAILABLE and candidate_skills and job_skills:
        semantic = _embedding_similarity(candidate_skills, job_skills)
        score = 0.6 * base_score + 0.4 * semantic
    else:
        score = base_score
    
    return round(min(score, 1.0), 3), matched, missing


def rank_candidates(
    candidates: List[Dict],  # [{id, name, skills: [...]}]
    job_skills: List[str]
) -> List[Dict]:
    """Rank and score all candidates for a job. Returns sorted list."""
    results = []
    for candidate in candidates:
        score, matched, missing = compute_match_score(
            candidate.get("skills", []), job_skills
        )
        results.append({
            "id": candidate["id"],
            "name": candidate["name"],
            "email": candidate.get("email", ""),
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
        })
    
    # Sort by score descending
    return sorted(results, key=lambda x: x["match_score"], reverse=True)
