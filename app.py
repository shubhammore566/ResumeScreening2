"""Streamlit app — Resume Screening with Experience + Academic Scoring
   + Academic-Query (SSC/HSC/CGPA) based Selection."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from resume_parser import parse_uploaded_resume

from scorer import (
    ResumeScore,
    build_recommendation,
    calculate_ats_score,
    calculate_academic_score,
    calculate_academic_selection_score,
    calculate_experience_score,
    calculate_overall_score,
    calculate_similarity_score,
    rank_resumes,
    rank_resumes_by_academics,
)

from skill_extractor import (
    create_resume_summary,
    experience_label,
    extract_academic_marks,
    extract_experience_years,
    extract_free_text_keywords,
    extract_skills,
    extract_skills_from_job_description,
    get_missing_skills,
    is_academic_query,
    keyword_search_in_text,
)


st.set_page_config(
    page_title="AI Resume Screening Agent",
    page_icon="📄",
    layout="wide",
)

if "results" not in st.session_state:
    st.session_state.results = None
if "ranking_df" not in st.session_state:
    st.session_state.ranking_df = None
if "required_skills" not in st.session_state:
    st.session_state.required_skills = None
if "academic_mode" not in st.session_state:
    st.session_state.academic_mode = False


CUSTOM_CSS = """
<style>
.main { background: #f7f9fc; }
.hero {
    padding: 1.3rem 1.5rem;
    border-radius: 8px;
    background: linear-gradient(135deg, #102a43, #1d4ed8);
    color: white;
    margin-bottom: 1rem;
}
.hero h1 { margin: 0; font-size: 2rem; }
.hero p  { margin: .35rem 0 0; color: #dbeafe; }
.score-card {
    padding: 1rem;
    border-radius: 8px;
    background: white;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 6px rgba(15,23,42,0.08);
}
.best-badge {
    background: #16a34a;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: bold;
}
.academic-badge {
    background: #7c3aed;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: bold;
}
</style>
"""


def render_score_card(title: str, value: float, suffix: str = "%") -> None:
    st.markdown(
        f"""<div class="score-card">
            <h3>{title}</h3>
            <strong>{value:.2f}{suffix}</strong>
        </div>""",
        unsafe_allow_html=True,
    )


def plot_skill_match(matched_skills, missing_skills):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(["Matched Skills", "Missing Skills"],
           [len(matched_skills), len(missing_skills)],
           color=["#16a34a", "#dc2626"])
    ax.set_ylabel("Count")
    ax.set_title("Skill Match Overview")
    st.pyplot(fig)


def plot_skill_distribution(matched_skills, missing_skills):
    values = [len(matched_skills), len(missing_skills)]
    if sum(values) == 0:
        st.info("No skills found.")
        return
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(values, labels=["Matched", "Missing"],
           autopct="%1.1f%%", startangle=90,
           colors=["#22c55e", "#f97316"])
    ax.set_title("Skill Match %")
    st.pyplot(fig)


def plot_experience_bar(results: list[ResumeScore]) -> None:
    """Bar chart — experience years comparison across all resumes."""
    names  = [r.filename for r in results]
    years  = [r.experience_years for r in results]
    colors = ["#1d4ed8" if y == max(years) else "#93c5fd" for y in years]

    fig, ax = plt.subplots(figsize=(max(5, len(names) * 1.5), 3))
    bars = ax.bar(names, years, color=colors)
    ax.set_ylabel("Experience (years)")
    ax.set_title("Experience Comparison")
    ax.set_ylim(0, max(years) + 2 if years else 5)

    for bar, yr in zip(bars, years):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{yr} yrs", ha="center", fontsize=9)

    plt.xticks(rotation=20, ha="right")
    st.pyplot(fig)


def plot_academic_bar(results: list[ResumeScore]) -> None:
    """Bar chart — academic score comparison across all resumes."""
    names  = [r.filename for r in results]
    scores = [r.academic_score for r in results]
    colors = ["#7c3aed" if s == max(scores) else "#c4b5fd" for s in scores]

    fig, ax = plt.subplots(figsize=(max(5, len(names) * 1.5), 3))
    bars = ax.bar(names, scores, color=colors)
    ax.set_ylabel("Academic Score")
    ax.set_title("Academic Score Comparison (10th / 12th / CGPA)")
    ax.set_ylim(0, 100)

    for bar, sc in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{sc:.1f}", ha="center", fontsize=9)

    plt.xticks(rotation=20, ha="right")
    st.pyplot(fig)


def analyze_resume(uploaded_file, job_description, required_skills) -> ResumeScore:
    parsed = parse_uploaded_resume(uploaded_file)

    matched_skills   = extract_skills(parsed.text, required_skills)
    missing_skills   = get_missing_skills(matched_skills, required_skills)
    experience_years = extract_experience_years(parsed.text)
    academic_marks    = extract_academic_marks(parsed.text)

    ats_score        = calculate_ats_score(matched_skills, required_skills)
    similarity_score = calculate_similarity_score(parsed.text, job_description, matched_skills, required_skills)
    experience_score = calculate_experience_score(experience_years)
    academic_score    = calculate_academic_score(academic_marks)
    overall_score     = calculate_overall_score(ats_score, similarity_score, experience_score, academic_score)
    academic_selection_score = calculate_academic_selection_score(academic_score, experience_score)

    summary          = create_resume_summary(parsed.text)
    recommendation   = build_recommendation(ats_score, similarity_score, experience_years, missing_skills)

    return ResumeScore(
        filename=parsed.filename,
        ats_score=ats_score,
        similarity_score=similarity_score,
        experience_score=experience_score,
        experience_years=experience_years,
        academic_score=academic_score,
        academic_marks=academic_marks,
        overall_score=overall_score,
        academic_selection_score=academic_selection_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        summary=summary,
        recommendation=recommendation,
        resume_text=parsed.text,
    )


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("""
        <div class="hero">
            <h1>Smart Resume Screening System</h1>
            <p>Resume parsing · ATS scoring · Experience scoring · Academic scoring (SSC/HSC/CGPA) · Job matching & ranking</p>
        </div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.header("Screening Setup")
        uploaded_files = st.file_uploader(
            "Upload PDF resumes", type=["pdf"], accept_multiple_files=True)
        job_description = st.text_area(
            "Paste job description OR type a query (e.g. 'ssc hsc', 'python developer', 'cgpa')",
            height=120,
            placeholder="e.g. data science / python developer / frontend  —  OR  —  ssc hsc / 10th 12th marks",
        )
        use_job_skills = st.checkbox("Use skills detected from job description", value=True)
        analyze_button = st.button("Analyze Resumes", type="primary", use_container_width=True)

    # ── DETECT QUERY TYPE ────────────────────────────────────────────────────
    # Agar description box mein "ssc"/"hsc"/"10th"/"12th"/"cgpa"/"marks" jaise
    # academic words likhe hain, to app academic-selection mode mein chala
    # jaata hai — yahan skill-matching zaroori nahi hai.
    academic_mode = is_academic_query(job_description)

    base_required_skills = (
        extract_skills_from_job_description(job_description) if use_job_skills else []
    )
    required_skills = base_required_skills

    if not required_skills and not academic_mode:
        st.warning(
            "No skills detected. Please enter a job description (e.g. 'data science', "
            "'frontend', 'python') — or type 'ssc'/'hsc'/'10th'/'12th'/'cgpa' to select "
            "candidates by academic marks instead."
        )
        st.stop()

    if academic_mode:
        st.subheader("🎓 Academic Selection Mode Active")
        st.info(
            "Description box mein academic keyword (SSC/HSC/10th/12th/CGPA) detect hua hai. "
            "Resumes ab academic marks (10th + 12th + CGPA overall) ke basis par select/rank "
            "kiye jaayenge — jisme sabse zyada marks honge, wahi resume top pe select hoga."
        )
        if required_skills:
            st.subheader("Additionally Detected Skills")
            st.success(", ".join(required_skills))
    else:
        st.subheader("Required Skills")
        st.success(", ".join(required_skills))

    # ── ANALYZE ──────────────────────────────────────────────────────────────
    if analyze_button:
        if not uploaded_files:
            st.error("Please upload at least one PDF resume.")
            st.stop()

        results = []
        progress_bar = st.progress(0)
        for i, uploaded_file in enumerate(uploaded_files, 1):
            try:
                result = analyze_resume(uploaded_file, job_description, required_skills)
                results.append(result)
            except Exception as e:
                st.warning(f"Could not analyze {uploaded_file.name}: {e}")
            progress_bar.progress(i / len(uploaded_files))

        if not results:
            st.error("No resumes could be analyzed.")
            st.stop()

        st.session_state.results      = results
        st.session_state.ranking_df   = rank_resumes(results)
        st.session_state.required_skills = required_skills
        st.session_state.academic_mode = academic_mode

    # ── LOAD RESULTS ──────────────────────────────────────────────────────────
    if st.session_state.results is None:
        st.info("Upload resumes and click Analyze Resumes.")
        st.stop()

    results      = st.session_state.results
    ranking_df   = st.session_state.ranking_df
    required_skills = st.session_state.required_skills
    academic_mode = st.session_state.academic_mode

    # Selection logic:
    #   - Academic-query mode (SSC/HSC/CGPA typed)  → highest academic_selection_score wins
    #     (10th + 12th + CGPA overall marks, with a small experience boost)
    #   - Normal job-description mode               → highest overall_score wins
    #     (ATS + similarity + experience + academic)
    if academic_mode:
        best = max(results, key=lambda r: r.academic_selection_score)
    else:
        best = max(results, key=lambda r: r.overall_score)

    # ── TOP SNAPSHOT ──────────────────────────────────────────────────────────
    st.subheader("🏆 Best Candidate Snapshot")
    if academic_mode:
        st.markdown(
            f'<span class="academic-badge">🎓 Selected: {best.filename} — Academic Score: '
            f'{best.academic_score:.1f} — {best.experience_years} yrs experience</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<span class="best-badge">⭐ Best: {best.filename} — {best.experience_years} yrs experience — '
            f'Academic Score: {best.academic_score:.1f}</span>',
            unsafe_allow_html=True
        )
    st.write("")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: render_score_card("ATS Score",        best.ats_score)
    with col2: render_score_card("Job Match",        best.similarity_score)
    with col3: render_score_card("Experience Score", best.experience_score)
    with col4: render_score_card("Academic Score",   best.academic_score)
    with col5: render_score_card("Overall Score",    best.overall_score)

    # ── ACADEMIC-BASED SELECTION (SSC / HSC / CGPA) ──────────────────────────
    # Ye section sirf tab dikhta hai jab description box mein academic query
    # (ssc/hsc/10th/12th/cgpa/marks) type ki gayi ho. Sabse zyada marks wale
    # candidate ko "✅ Selected" badge milta hai.
    if academic_mode:
        st.subheader("🎓 Academic-Based Selection (SSC / HSC / CGPA)")
        academic_rank_df = rank_resumes_by_academics(results)
        academic_rank_df.insert(
            1, "Selected",
            academic_rank_df["Student Name"].apply(lambda n: "✅" if n == best.filename else "")
        )
        st.dataframe(academic_rank_df, use_container_width=True, hide_index=True)
        st.success(
            f"✅ Highest overall marks (10th + 12th + CGPA): **{best.filename}** "
            f"— Academic Score: {best.academic_score:.1f}/100, "
            f"Experience: {best.experience_years} yrs"
        )

    # ── EXPERIENCE COMPARISON ─────────────────────────────────────────────────
    st.subheader("📅 Experience Comparison")
    plot_experience_bar(results)

    exp_sorted = sorted(results, key=lambda r: r.experience_years, reverse=True)
    st.markdown("**Experience Summary:**")
    for r in exp_sorted:
        label = experience_label(r.experience_years)
        badge = "🥇" if r == best else "📄"
        st.write(f"{badge} **{r.filename}** — {label}")

    # ── ACADEMIC COMPARISON ───────────────────────────────────────────────────
    st.subheader("🎓 Academic Score Comparison")
    plot_academic_bar(results)

    acad_sorted = sorted(results, key=lambda r: r.academic_score, reverse=True)
    st.markdown("**Academic Summary (10th / 12th / CGPA):**")
    for r in acad_sorted:
        m = r.academic_marks or {}
        parts = []
        if m.get("tenth") is not None:
            parts.append(f"10th: {m['tenth']}%")
        if m.get("twelfth") is not None:
            parts.append(f"12th: {m['twelfth']}%")
        if m.get("cgpa") is not None:
            parts.append(f"CGPA: {m['cgpa']}/{m.get('cgpa_scale', 10.0):.0f}")
        detail = " | ".join(parts) if parts else "No academic marks detected"
        badge = "🥇" if r == best else "📄"
        st.write(f"{badge} **{r.filename}** — Score: {r.academic_score:.1f} — {detail}")

    # ── STUDENT-WISE MARKS (separate, per-student) ────────────────────────────
    st.subheader("👤 Student-wise Marks")
    marks_rows = []
    for r in results:
        m = r.academic_marks or {}
        marks_rows.append({
            "Student Name": r.filename,
            "10th %": m.get("tenth") if m.get("tenth") is not None else "-",
            "12th %": m.get("twelfth") if m.get("twelfth") is not None else "-",
            "CGPA": (
                f"{m['cgpa']}/{m.get('cgpa_scale', 10.0):.0f}"
                if m.get("cgpa") is not None else "-"
            ),
            "Academic Score": r.academic_score,
        })
    st.dataframe(pd.DataFrame(marks_rows), use_container_width=True, hide_index=True)

    # ── KEYWORD SEARCH FROM DESCRIPTION BOX ───────────────────────────────────
    # Description box mein jo bhi word likha ho (skill ho, "SSC"/"HSC" ho, ya
    # koi bhi other term ho) — us word ko har resume ke pure text mein dhoondo
    # aur jin resumes/students mein wo mila unka naam yahan dikhao.
    st.subheader("🔎 Keyword Search (from Description Box)")
    desc_keywords = extract_free_text_keywords(job_description)
    if not desc_keywords:
        st.info("Description box mein koi searchable word nahi mila.")
    else:
        keyword_rows = []
        for r in results:
            matched_kw = keyword_search_in_text(r.resume_text, desc_keywords)
            if matched_kw:
                keyword_rows.append({
                    "Student Name": r.filename,
                    "Matched Words": ", ".join(matched_kw),
                })
        if keyword_rows:
            st.success(f"Searched words: {', '.join(desc_keywords)}")
            st.dataframe(pd.DataFrame(keyword_rows), use_container_width=True, hide_index=True)
        else:
            st.warning(f"Description ke words ({', '.join(desc_keywords)}) kisi bhi resume mein nahi mile.")

    # ── RANKING TABLE ─────────────────────────────────────────────────────────
    st.subheader("📊 Resume Ranking")
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)

    # ── DETAILED ANALYSIS ─────────────────────────────────────────────────────
    st.subheader("🔍 Detailed Resume Analysis")
    selected_resume = st.selectbox("Choose resume", [r.filename for r in results])
    sel = next(r for r in results if r.filename == selected_resume)

    d1, d2 = st.columns([1.5, 1])
    with d1:
        st.markdown("### Experience")
        st.info(f"**{experience_label(sel.experience_years)}**  |  Experience Score: {sel.experience_score}/100")

        st.markdown("### Academics")
        m = sel.academic_marks or {}
        acad_parts = []
        if m.get("tenth") is not None:
            acad_parts.append(f"10th: {m['tenth']}%")
        if m.get("twelfth") is not None:
            acad_parts.append(f"12th: {m['twelfth']}%")
        if m.get("cgpa") is not None:
            acad_parts.append(f"CGPA: {m['cgpa']}/{m.get('cgpa_scale', 10.0):.0f}")
        acad_detail = " | ".join(acad_parts) if acad_parts else "No academic marks detected"
        st.info(
            f"**{acad_detail}**  |  Academic Score: {sel.academic_score}/100  |  "
            f"Academic Selection Score: {sel.academic_selection_score}/100"
        )

        st.markdown("### Matched Skills")
        st.success(", ".join(sel.matched_skills) or "No matching skills found.")

        st.markdown("### Missing Skills")
        st.warning(", ".join(sel.missing_skills) or "No missing skills.")

        st.markdown("### Recommendation")
        st.info(sel.recommendation)

    with d2:
        plot_skill_match(sel.matched_skills, sel.missing_skills)
        plot_skill_distribution(sel.matched_skills, sel.missing_skills)

    # ── COMPARISON CHART ──────────────────────────────────────────────────────
    st.subheader("📈 Comparison Chart")
    chart_data = ranking_df[["Resume", "ATS Score", "Experience Score", "Academic Score", "Overall Score"]].set_index("Resume")
    st.bar_chart(chart_data)

    # ── DOWNLOAD ──────────────────────────────────────────────────────────────
    csv_data = ranking_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Ranking CSV", data=csv_data,
                       file_name="resume_ranking.csv", mime="text/csv")


if __name__ == "__main__":
    main()
