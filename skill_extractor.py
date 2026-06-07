"""Skill extraction utilities for the resume screening agent.

The extractor is intentionally offline and beginner-friendly. It uses a
curated skill dictionary with regex matching instead of calling an AI API.
"""

from __future__ import annotations

import re
from typing import Iterable

import spacy


# The required skills can be edited or expanded for a specific job role.
DEFAULT_SKILLS = [
    "Python",
    "SQL",
    "Power BI",
    "Tableau",
    "Machine Learning",
    "NLP",
    "Excel",
    "Data Analysis",
    "Deep Learning",
]


# Common aliases help catch wording differences in resumes.
SKILL_ALIASES = {
    "Python": [r"python"],
    "SQL": [r"sql", r"mysql", r"postgresql", r"postgres", r"sqlite", r"ms sql", r"sql server"],
    "Power BI": [r"power\s*bi", r"powerbi"],
    "Tableau": [r"tableau"],
    "Machine Learning": [r"machine\s+learning", r"\bml\b"],
    "NLP": [r"\bnlp\b", r"natural\s+language\s+processing"],
    "Excel": [r"excel", r"microsoft\s+excel", r"spreadsheet"],
    "Data Analysis": [r"data\s+analysis", r"data\s+analytics", r"analytics"],
    "Deep Learning": [r"deep\s+learning", r"neural\s+network", r"neural\s+networks", r"\bdl\b"],
}


try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    # This keeps the app usable even when the optional spaCy model is not
    # installed. The project still uses spaCy for tokenization offline.
    NLP = spacy.blank("en")
    NLP.add_pipe("sentencizer")


def normalize_text(text: str) -> str:
    """Clean text for consistent matching."""
    text = text or ""
    return re.sub(r"\s+", " ", text).strip()


def extract_skills(text: str, required_skills: Iterable[str] | None = None) -> list[str]:
    """Return skills found in the resume text.

    Args:
        text: Resume text extracted from a PDF.
        required_skills: Optional custom skill list from a job description.
    """
    normalized = normalize_text(text).lower()
    skills_to_check = list(required_skills or DEFAULT_SKILLS)
    found_skills: list[str] = []

    for skill in skills_to_check:
        patterns = SKILL_ALIASES.get(skill, [re.escape(skill.lower())])
        if any(re.search(rf"(?<!\w){pattern}(?!\w)", normalized) for pattern in patterns):
            found_skills.append(skill)

    return sorted(set(found_skills), key=str.lower)


def extract_skills_from_job_description(job_description: str) -> list[str]:
    """Find default required skills mentioned in a job description."""
    return extract_skills(job_description, DEFAULT_SKILLS)


def get_missing_skills(found_skills: Iterable[str], required_skills: Iterable[str]) -> list[str]:
    """Return required skills that were not found in the resume."""
    found_set = {skill.lower() for skill in found_skills}
    return [skill for skill in required_skills if skill.lower() not in found_set]


def create_resume_summary(text: str, max_sentences: int = 3) -> str:
    """Create a short extractive summary from the resume text.

    This is a simple offline summary. It chooses the first few meaningful
    sentences, which usually contain profile, education, or experience details.
    """
    cleaned = normalize_text(text)
    if not cleaned:
        return "No readable text was found in this resume."

    doc = NLP(cleaned)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 30]

    if not sentences:
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        sentences = [sentence.strip() for sentence in sentences if len(sentence.strip()) > 30]

    summary = " ".join(sentences[:max_sentences])
    return summary or cleaned[:450]
