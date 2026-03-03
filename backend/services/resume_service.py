"""
Resume Parser Service
======================
Extracts text from uploaded resume files (PDF, DOCX, TXT).
Uses PyPDF2 for basic PDF parsing and pdfminer for advanced extraction.
"""

import os
import re
from typing import Dict, Optional

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyPDF2 with pdfminer fallback."""
    text = ""

    # Try PyPDF2 first
    try:
        import pypdf
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        if text.strip():
            return text
    except Exception as e:
        pass

    # Fallback: pdfminer
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        text = pdfminer_extract(file_path)
        return text or ""
    except Exception as e:
        pass

    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX files using python-docx."""
    try:
        import docx
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return ""


def extract_text(file_path: str) -> str:
    """Auto-detect file type and extract text."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def parse_sections(text: str) -> Dict:
    """
    Parse resume text into sections: name, contact, education, experience, skills.
    Uses heuristic regex patterns.
    """
    sections = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": extract_section(text, ["education", "academic", "degree", "university", "college"]),
        "experience": extract_section(text, ["experience", "work history", "employment", "projects"]),
        "skills_section": extract_section(text, ["skills", "technical skills", "technologies", "tools"]),
    }
    return sections


def extract_name(text: str) -> str:
    """Extract candidate name (first non-empty line, usually)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        # First line often contains name — basic heuristic
        first_line = lines[0]
        if len(first_line.split()) <= 5 and not "@" in first_line:
            return first_line
    return "Unknown"


def extract_email(text: str) -> str:
    """Extract email address from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group() if match else ""


def extract_phone(text: str) -> str:
    """Extract phone number from text."""
    pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    match = re.search(pattern, text)
    return match.group() if match else ""


def extract_section(text: str, keywords: list) -> str:
    """Extract a named section from resume text."""
    lines = text.split("\n")
    capturing = False
    section_lines = []
    section_end_keywords = ["education", "experience", "skills", "projects", "certifications",
                             "awards", "languages", "interests", "objective", "summary"]

    for line in lines:
        line_lower = line.lower().strip()

        # Check if this line is a section header we want
        if any(kw in line_lower for kw in keywords) and len(line.strip()) < 50:
            capturing = True
            continue

        # Check if we've hit a different section header
        if capturing and any(kw in line_lower for kw in section_end_keywords):
            if not any(kw in line_lower for kw in keywords):
                break

        if capturing and line.strip():
            section_lines.append(line.strip())

    return " ".join(section_lines[:10])  # Limit to first 10 lines of section
