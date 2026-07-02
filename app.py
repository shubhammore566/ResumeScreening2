"""Scoring, matching, and recommendation logic — with experience + academic scoring."""

from __future__ import annotations

from dataclasses import dataclass, field

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
    academic_score: float
    academic_marks: dict = field(default_factory=dict)
    overall_score: float = 0.0
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    summary: str = ""
    recommendation: str = ""


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


def calculate_academic_score(marks: dict) -> float:
    """
    10th %, 12th % aur CGPA ko 0-100 academic score mein convert karo.
    Jitna high marks, utna high score — high score wale candidate ki
    ranking/selection priority zyada hogi.

    marks = {"tenth": float|None, "twelfth": float|None,
             "cgpa": float|None, "cgpa_scale": float}
    """
    components = []

    if marks.get("tenth") is not None:
        components.append(marks["tenth"])

    if marks.get("twelfth") is not None:
        components.append(marks["twelfth"])

    if marks.get("cgpa") is not None:
        scale = marks.get("cgpa_scale", 10.0) or 10.0
        cgpa_percent = (marks["cgpa"] / scale) * 100
        components.append(cgpa_percent)

    if not components:
        return 0.0

    academic_score = sum(components) / len(components)
    return round(min(academic_score, 100), 2)


def calculate_overall_score(
        ats_score: float,
        similarity_score: float,
        experience_score: float,
        academic_score: float
) -> float:
    """
    Weights:
      ATS Score         → 25%
      Similarity Score  → 35%
      Experience Score  → 15%
      Academic Score    → 25%
    """
    overall = (
        (ats_score * 0.25)
        + (similarity_score * 0.35)
        + (experience_score * 0.15)
        + (academic_score * 0.25)
    )
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
            "Academic Score": r.academic_score,
            "Overall Score": r.overall_score,
            "Matched Skills": ", ".join(r.matched_skills) or "None",
            "Missing Skills": ", ".join(r.missing_skills) or "None",
        }
        for i, r in enumerate(
            sorted(results, key=lambda x: x.overall_score, reverse=True)
        )
    ]
    return pd.DataFrame(rows)
