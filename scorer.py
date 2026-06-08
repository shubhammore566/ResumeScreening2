"""Scoring, matching, and recommendation logic — with experience scoring."""

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
    experience_score: float
    experience_years: float
    overall_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    summary: str
    recommendation: str


def calculate_ats_score(matched_skills: list[str], required_skills: list[str]) -> float:
    if not required_skills:
        return 0.0
    skill_ratio = len(matched_skills) / len(required_skills)
    ats_score = 50 + (skill_ratio * 35)
    return round(min(ats_score, 85), 2)


def calculate_similarity_score(
        resume_text: str,
        job_description: str,
        matched_skills: list[str],
        required_skills: list[str]
) -> float:
    if not resume_text.strip() or not job_description.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([resume_text, job_description])
    text_score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100

    skill_ratio = len(matched_skills) / len(required_skills) if required_skills else 0

    if skill_ratio >= 1:
        similarity_score = 95 + (text_score * 0.05)
    elif skill_ratio >= 0.8:
        similarity_score = 85 + (text_score * 0.08)
    elif skill_ratio >= 0.6:
        similarity_score = 70 + (text_score * 0.10)
    else:
        similarity_score = (skill_ratio * 70) + (text_score * 0.30)

    return round(min(similarity_score, 100), 2)


def calculate_experience_score(years: float) -> float:
    """
    Experience years ko 0-100 score mein convert karo.

    0 yrs  → 0
    1 yr   → 20  (fresher)
    2 yrs  → 35
    3 yrs  → 50
    5 yrs  → 70
    7 yrs  → 85
    10+ yrs→ 100
    """
    if years <= 0:
        return 0.0
    elif years <= 1:
        score = years * 20
    elif years <= 3:
        score = 20 + (years - 1) * 15
    elif years <= 5:
        score = 50 + (years - 3) * 10
    elif years <= 7:
        score = 70 + (years - 5) * 7.5
    elif years <= 10:
        score = 85 + (years - 7) * 5
    else:
        score = 100.0

    return round(min(score, 100), 2)


def calculate_overall_score(
        ats_score: float,
        similarity_score: float,
        experience_score: float
) -> float:
    """
    Weights:
      ATS Score        → 35%
      Similarity Score → 45%
      Experience Score → 20%
    """
    overall = (ats_score * 0.35) + (similarity_score * 0.45) + (experience_score * 0.20)
    return round(min(overall, 100), 2)


def build_recommendation(
        ats_score: float,
        similarity_score: float,
        experience_years: float,
        missing_skills: list[str]
) -> str:
    exp_note = ""
    if experience_years == 0:
        exp_note = " No work experience detected — may be a fresher."
    elif experience_years < 2:
        exp_note = f" Candidate has {experience_years} yr(s) experience — junior level."
    else:
        exp_note = f" Candidate has {experience_years} yrs experience."

    if ats_score >= 80 and similarity_score >= 45:
        return f"Strong match. Resume covers most required skills and aligns well with the job description.{exp_note}"

    if ats_score >= 60:
        missing_text = ", ".join(missing_skills) if missing_skills else "job-specific keywords"
        return f"Good potential match. Improve resume by adding: {missing_text}.{exp_note}"

    missing_text = ", ".join(missing_skills) if missing_skills else "the required role skills"
    return f"Needs improvement. Candidate should strengthen: {missing_text}.{exp_note}"


def rank_resumes(results: list[ResumeScore]) -> pd.DataFrame:
    """Return ranking table sorted by overall score."""
    rows = [
        {
            "Rank": i + 1,
            "Resume": r.filename,
            "Experience": f"{r.experience_years} yrs",
            "ATS Score": r.ats_score,
            "Similarity Score": r.similarity_score,
            "Experience Score": r.experience_score,
            "Overall Score": r.overall_score,
            "Matched Skills": ", ".join(r.matched_skills) or "None",
            "Missing Skills": ", ".join(r.missing_skills) or "None",
        }
        for i, r in enumerate(
            sorted(results, key=lambda x: x.overall_score, reverse=True)
        )
    ]
    return pd.DataFrame(rows)
