"""Scoring, matching, and recommendation logic."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class ResumeScore:
    """A complete score result for one resume."""

    filename: str
    ats_score: float
    similarity_score: float
    overall_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    summary: str
    recommendation: str


def calculate_ats_score(matched_skills: list[str], required_skills: list[str]) -> float:
    """Calculate ATS score as the percentage of required skills found."""
    if not required_skills:
        return 0.0
    return round((len(matched_skills) / len(required_skills)) * 100, 2)


def calculate_similarity_score(resume_text: str, job_description: str) -> float:
    """Compare resume and job description using TF-IDF cosine similarity."""
    if not resume_text.strip() or not job_description.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([resume_text, job_description])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def calculate_overall_score(ats_score: float, similarity_score: float) -> float:
    """Combine skill coverage and job-description similarity."""
    return round((ats_score * 0.65) + (similarity_score * 0.35), 2)


def build_recommendation(ats_score: float, similarity_score: float, missing_skills: list[str]) -> str:
    """Create a practical recommendation based on the scores."""
    if ats_score >= 80 and similarity_score >= 45:
        return "Strong match. This resume covers most required skills and aligns well with the job description."

    if ats_score >= 60:
        missing_text = ", ".join(missing_skills) if missing_skills else "job-specific keywords"
        return f"Good potential match. Improve the resume by adding clearer evidence for: {missing_text}."

    missing_text = ", ".join(missing_skills) if missing_skills else "the required role skills"
    return f"Needs improvement. The candidate should strengthen or highlight these skills: {missing_text}."


def rank_resumes(results: list[ResumeScore]) -> pd.DataFrame:
    """Return a ranking table sorted by overall score."""
    rows = [
        {
            "Rank": index + 1,
            "Resume": result.filename,
            "ATS Score": result.ats_score,
            "Similarity Score": result.similarity_score,
            "Overall Score": result.overall_score,
            "Matched Skills": ", ".join(result.matched_skills) or "None",
            "Missing Skills": ", ".join(result.missing_skills) or "None",
        }
        for index, result in enumerate(sorted(results, key=lambda item: item.overall_score, reverse=True))
    ]
    return pd.DataFrame(rows)
