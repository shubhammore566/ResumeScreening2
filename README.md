<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=Resume%20Screening%20System&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=NLP%20%7C%20TF-IDF%20%7C%20Resume%20Ranking%20%7C%20ATS%20Score&descAlignY=55&descSize=18" width="100%"/>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&duration=3000&pause=800&color=00B894,6C5CE7,FD79A8,FDCB6E,0984E3&center=true&vCenter=true&multiline=true&repeat=true&width=750&height=90&lines=%F0%9F%93%84+AI-Powered+Resume+Screening+System;Rank+Resumes+Against+Job+Descriptions;Smart+ATS+Score+%2B+Keyword+Matching" alt="Typing SVG" />
</a>

<br/><br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-6C5CE7?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00B894?style=for-the-badge)

</div>

---

### 📄 About The Project

**Resume Screening System** is an NLP-based application that automatically screens, ranks, and scores resumes against a given job description — just like a real **Applicant Tracking System (ATS)**.

It helps recruiters shortlist the most relevant candidates in seconds instead of manually reading hundreds of resumes, and helps job seekers check how well their resume matches a job posting before applying.

```yaml
Project:      Resume Screening System
Type:         NLP · Text Classification · Information Retrieval
Goal:         Rank resumes by relevance to a job description
Output:       Ranked resume list + ATS match score (%)
```

---

### ✨ Key Features

- 📂 **Bulk Resume Upload** — Upload multiple resumes (PDF/DOCX) at once
- 🧠 **NLP Text Extraction & Cleaning** — Tokenization, stopword removal, lemmatization
- 🔢 **TF-IDF Vectorization** — Converts resume & job description text into numeric vectors
- 📊 **Cosine Similarity Ranking** — Ranks resumes by relevance to the job description
- 🎯 **ATS Score** — Gives each resume a match percentage score
- 🏆 **Top Candidate Shortlist** — Instantly view the best-matching resumes
- 📈 **Interactive Dashboard** — Clean, visual results built with Streamlit

---

### 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![NLTK](https://img.shields.io/badge/NLTK-154F5B?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

</div>

---

### ⚙️ How It Works

```mermaid
flowchart LR
    A[📂 Upload Resumes + Job Description] --> B[🧹 Text Cleaning & Preprocessing]
    B --> C[🔢 TF-IDF Vectorization]
    C --> D[📐 Cosine Similarity Scoring]
    D --> E[🏆 Ranked Resumes + ATS Score]
```

1. **Input** — Upload resumes (PDF/DOCX) along with a job description
2. **Preprocessing** — Text is cleaned: lowercasing, stopword removal, lemmatization
3. **Vectorization** — TF-IDF converts text into numerical feature vectors
4. **Scoring** — Cosine similarity compares each resume vector to the job description vector
5. **Ranking** — Resumes are sorted by similarity/ATS score, highest match first

---

### 🚀 Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/shubhammore566/resume-screening-system.git
cd resume-screening-system
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run app.py
```

---

### 📂 Project Structure

```
resume-screening-system/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── data/                  # Sample resumes / job descriptions
├── utils/                 # Text preprocessing & scoring functions
└── README.md              # Project documentation
```

---

### 📈 Sample Output

| Rank | Candidate Resume | ATS Match Score |
|------|-------------------|:----------------:|
| 🥇 1  | resume_john.pdf    | 92%              |
| 🥈 2  | resume_priya.pdf   | 87%              |
| 🥉 3  | resume_alex.pdf    | 79%              |
| 4    | resume_maria.pdf   | 65%              |

---

### 🔮 Future Improvements

- 🤖 Use **BERT / Sentence Transformers** for semantic similarity (beyond TF-IDF)
- 📑 Add support for scanned/image-based resumes via OCR
- 🌐 Deploy as a public web app
- 📊 Add skill-gap analysis for each candidate

---

### 📫 Connect With Me

<div align="center">

[![Gmail](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:shubhammore976525@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/shubham-more-a749b1333)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/shubhammore566)

⭐ **If you found this project useful, don't forget to star the repo!**

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer"/>

</div>
