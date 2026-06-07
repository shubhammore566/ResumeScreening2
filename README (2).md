# AI-Powered Resume Screening Agent

This project is a complete offline resume screening app built with Python. It does not use OpenAI, Gemini, Claude, external APIs, API keys, or paid AI services.

## Features

- Upload one or more PDF resumes.
- Extract text from PDFs with `pdfplumber`.
- Detect skills such as Python, SQL, Power BI, Tableau, Machine Learning, NLP, Excel, Data Analysis, and Deep Learning.
- Calculate an ATS score from matched required skills.
- Compare resumes with a job description using TF-IDF and cosine similarity from `scikit-learn`.
- Rank multiple resumes by combined score.
- Show extracted skills, missing skills, summary, recommendation, charts, and downloadable CSV results.
- Run everything through a Streamlit dashboard.

## Folder Structure

```text
resume-screening-agent/
  app.py
  parser.py
  skill_extractor.py
  scorer.py
  requirements.txt
  README.md
```

## How It Works

1. `parser.py` reads uploaded PDF resumes and extracts text.
2. `skill_extractor.py` cleans text and finds skills using regex patterns and aliases.
3. `scorer.py` calculates ATS score, job-description similarity, overall score, ranking, and recommendations.
4. `app.py` provides the Streamlit interface, upload system, dashboards, charts, and CSV export.

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional: install the small spaCy English model for better sentence splitting:

```bash
python -m spacy download en_core_web_sm
```

The app still runs without this model because it falls back to `spacy.blank("en")`.

## Run Command

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Deployment Guidance

You can deploy this project to Streamlit Community Cloud or any Python server that supports Streamlit.

For Streamlit Community Cloud:

1. Push this folder to a GitHub repository.
2. Create a new Streamlit app.
3. Select `app.py` as the entry file.
4. Make sure `requirements.txt` is included.
5. Deploy.

No secrets or API keys are required.

## Customization

Edit `DEFAULT_SKILLS` and `SKILL_ALIASES` in `skill_extractor.py` to add more job-specific skills or alternate spellings.
