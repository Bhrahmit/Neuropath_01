"""
Resume Parser Service
=====================
Extracts text from PDF/DOCX resumes using PyPDF2 and pdfminer.
Also parses sections: education, experience, skills.
"""

import re
import io
from typing import Tuple, Dict

# PDF extraction
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text as pdfminer_extract
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes. Tries PyPDF2 first, falls back to pdfminer."""
    text = ""
    
    if PYPDF_AVAILABLE:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception:
            pass
    
    # If PyPDF2 gave too little text, try pdfminer
    if len(text.strip()) < 100 and PDFMINER_AVAILABLE:
        try:
            text = pdfminer_extract(io.BytesIO(file_bytes))
        except Exception:
            pass
    
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX files using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Route to appropriate extractor based on file extension."""
    fname_lower = filename.lower()
    if fname_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif fname_lower.endswith((".docx", ".doc")):
        return extract_text_from_docx(file_bytes)
    elif fname_lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        # Try PDF as default
        return extract_text_from_pdf(file_bytes)


# ─── Section Parser ────────────────────────────────────────────────────────────

SECTION_HEADERS = {
    "education": r"(education|academic|qualifications|degree)",
    "experience": r"(experience|work history|employment|professional background)",
    "skills": r"(skills|technical skills|competencies|technologies)",
    "projects": r"(projects|portfolio|personal projects)",
    "certifications": r"(certifications|certificates|courses)",
    "summary": r"(summary|objective|profile|about me)",
}


def parse_sections(text: str) -> Dict[str, str]:
    """Split resume text into labelled sections."""
    lines = text.split("\n")
    sections = {}
    current_section = "other"
    current_lines = []
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        matched = False
        for section_name, pattern in SECTION_HEADERS.items():
            if re.search(pattern, line_clean, re.IGNORECASE) and len(line_clean) < 60:
                # Save previous section
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                current_section = section_name
                current_lines = []
                matched = True
                break
        
        if not matched:
            current_lines.append(line_clean)
    
    # Save last section
    if current_lines:
        sections[current_section] = "\n".join(current_lines)
    
    return sections
