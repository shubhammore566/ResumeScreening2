"""Streamlit app for the offline AI-powered Resume Screening Agent."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from parser import parse_uploaded_resume
from scorer import (
    ResumeScore,
    build_recommendation,
    calculate_ats_score,
    calculate_overall_score,
    calculate_similarity_score,
    rank_resumes,
)
from skill_extractor import (
    DEFAULT_SKILLS,
    create_resume_summary,
    extract_skills,
    extract_skills_from_job_description,
    get_missing_skills,
)


st.set_page_config(
    page_title="AI Resume Screening Agent",
    page_icon="AI",
    layout="wide",
)


CUSTOM_CSS = """
<style>
    .main {
        background: #f7f9fc;
    }
    .hero {
        padding: 1.3rem 1.5rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #102a43, #1d4ed8);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        margin: .35rem 0 0;
        color: #dbeafe;
    }
    .score-card {
        padding: 1rem;
        border-radius: 8px;
        background: white;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 6px rgba(15, 23, 42, 0.08);
    }
    .score-card h3 {
        margin: 0 0 .35rem;
        color: #334155;
        font-size: .95rem;
    }
    .score-card strong {
        color: #0f172a;
        font-size: 1.8rem;
    }
</style>
"""


def render_score_card(title: str, value: float, suffix: str = "%") -> None:
    """Render a compact metric card."""
    st.markdown(
        f"""
        <div class="score-card">
            <h3>{title}</h3>
            <strong>{value:.2f}{suffix}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plot_skill_match(matched_skills: list[str], missing_skills: list[str]) -> None:
    """Show a bar chart for matched vs missing skills."""
    labels = ["Matched Skills", "Missing Skills"]
    values = [len(matched_skills), len(missing_skills)]

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(labels, values, color=["#16a34a", "#dc2626"])
    ax.set_ylabel("Count")
    ax.set_title("Skill Match Overview")
    ax.set_ylim(0, max(values + [1]) + 1)
    st.pyplot(fig)


def plot_skill_distribution(matched_skills: list[str], missing_skills: list[str]) -> None:
    """Show a pie chart for matched and missing skills."""
    values = [len(matched_skills), len(missing_skills)]
    if sum(values) == 0:
        st.info("No required skills were found to visualize.")
        return

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        values,
        labels=["Matched", "Missing"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#22c55e", "#f97316"],
    )
    ax.set_title("Skill Match Percentage")
    st.pyplot(fig)


def analyze_resume(uploaded_file, job_description: str, required_skills: list[str]) -> ResumeScore:
    """Parse and score one uploaded resume."""
    parsed_resume = parse_uploaded_resume(uploaded_file)
    matched_skills = extract_skills(parsed_resume.text, required_skills)
    missing_skills = get_missing_skills(matched_skills, required_skills)
    ats_score = calculate_ats_score(matched_skills, required_skills)
    similarity_score = calculate_similarity_score(parsed_resume.text, job_description)
    overall_score = calculate_overall_score(ats_score, similarity_score)
    summary = create_resume_summary(parsed_resume.text)
    recommendation = build_recommendation(ats_score, similarity_score, missing_skills)

    return ResumeScore(
        filename=parsed_resume.filename,
        ats_score=ats_score,
        similarity_score=similarity_score,
        overall_score=overall_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        summary=summary,
        recommendation=recommendation,
    )


def main() -> None:
    """Run the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
            <h1>AI Resume Screening Agent</h1>
            <p>Offline resume parsing, skill extraction, ATS scoring, job matching, and ranking.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Screening Setup")
        uploaded_files = st.file_uploader(
            "Upload PDF resumes",
            type=["pdf"],
            accept_multiple_files=True,
        )
        job_description = st.text_area(
            "Paste job description",
            height=220,
            placeholder="Paste the role description, responsibilities, and required skills here.",
        )
        use_job_skills = st.checkbox("Use skills detected from job description", value=True)
        analyze_button = st.button("Analyze Resumes", type="primary", use_container_width=True)

    base_required_skills = extract_skills_from_job_description(job_description) if use_job_skills else []
    required_skills = base_required_skills or DEFAULT_SKILLS

    st.subheader("Required Skills")
    st.write(", ".join(required_skills))

    if not analyze_button:
        st.info("Upload one or more PDF resumes, paste a job description, then click Analyze Resumes.")
        return

    if not uploaded_files:
        st.error("Please upload at least one PDF resume.")
        return

    if not job_description.strip():
        st.error("Please paste a job description before analysis.")
        return

    results: list[ResumeScore] = []
    progress_bar = st.progress(0)

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        try:
            results.append(analyze_resume(uploaded_file, job_description, required_skills))
        except Exception as error:
            st.warning(f"Could not analyze {uploaded_file.name}: {error}")
        progress_bar.progress(index / len(uploaded_files))

    if not results:
        st.error("No resumes could be analyzed. Check that the PDFs contain selectable text.")
        return

    ranking_df = rank_resumes(results)
    best_result = max(results, key=lambda item: item.overall_score)

    st.subheader("Top Resume Snapshot")
    score_col_1, score_col_2, score_col_3 = st.columns(3)
    with score_col_1:
        render_score_card("ATS Score", best_result.ats_score)
    with score_col_2:
        render_score_card("Job Match", best_result.similarity_score)
    with score_col_3:
        render_score_card("Overall Score", best_result.overall_score)

    st.subheader("Resume Ranking")
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)

    st.subheader("Detailed Resume Analysis")
    selected_resume = st.selectbox("Choose resume", [result.filename for result in results])
    selected_result = next(result for result in results if result.filename == selected_resume)

    detail_col_1, detail_col_2 = st.columns([1.2, 1])
    with detail_col_1:
        st.markdown("#### Extracted Skills")
        st.success(", ".join(selected_result.matched_skills) or "No matching skills found.")

        st.markdown("#### Missing Skills")
        st.warning(", ".join(selected_result.missing_skills) or "No missing skills.")

        st.markdown("#### Resume Summary")
        st.write(selected_result.summary)

        st.markdown("#### Recommendation")
        st.info(selected_result.recommendation)

    with detail_col_2:
        plot_skill_match(selected_result.matched_skills, selected_result.missing_skills)
        plot_skill_distribution(selected_result.matched_skills, selected_result.missing_skills)

    st.subheader("Comparison Chart")
    chart_data = ranking_df[["Resume", "ATS Score", "Similarity Score", "Overall Score"]].set_index("Resume")
    st.bar_chart(chart_data)

    csv_data = ranking_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Ranking CSV",
        data=csv_data,
        file_name="resume_ranking.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
