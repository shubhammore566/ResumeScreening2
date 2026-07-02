"""Skill extraction utilities — no spacy dependency, with fuzzy role matching."""

from __future__ import annotations

import re
from typing import Iterable


DEFAULT_SKILLS = [
    "HTML", "CSS", "JavaScript", "React", "Angular", "Vue", "Bootstrap", "Tailwind CSS",
    "Python", "Java", "Node.js", "Django", "Flask", "Spring Boot",
    "SQL", "MySQL", "MongoDB", "PostgreSQL",
    "Machine Learning", "Deep Learning", "NLP", "Data Analysis",
    "Power BI", "Tableau", "Excel", "TensorFlow", "PyTorch",
    "Linux", "Docker", "Kubernetes", "AWS", "Azure", "CI/CD", "Jenkins", "Terraform",
    "Kotlin", "Firebase", "Swift", "Xcode", "Android Studio",
    "Figma", "UI/UX", "Wireframing", "Prototyping",
    "Selenium", "Automation Testing", "Manual Testing",
    "Networking", "Cyber Security", "Ethical Hacking", "Cisco", "Routing", "Switching",
    "Solidity", "Ethereum", "Blockchain", "Web3", "Unity", "C#", "Game Development", "Blender",
    "Git", "GitHub",
]


ROLE_SKILLS = {
    "frontend developer":       ["HTML","CSS","JavaScript","React","Angular","Vue","Bootstrap","Tailwind CSS","Git","GitHub"],
    "backend developer":        ["Python","Java","Node.js","Django","Flask","Spring Boot","SQL","MySQL","PostgreSQL","MongoDB","Git","GitHub"],
    "full stack developer":     ["HTML","CSS","JavaScript","React","Node.js","MongoDB","SQL","Git","GitHub"],
    "data analyst":             ["Python","SQL","Excel","Power BI","Tableau","Data Analysis"],
    "data scientist":           ["Python","Machine Learning","Deep Learning","NLP","SQL","Power BI","Tableau","Excel","TensorFlow","PyTorch","Git"],
    "machine learning engineer":["Python","Machine Learning","Deep Learning","TensorFlow","PyTorch","SQL","Git"],
    "ai engineer":              ["Python","Machine Learning","Deep Learning","NLP","TensorFlow","PyTorch","Git"],
    "devops engineer":          ["Linux","Docker","Kubernetes","AWS","CI/CD","Git","GitHub","Jenkins","Terraform"],
    "cloud engineer":           ["AWS","Azure","Docker","Kubernetes","Linux","Terraform"],
    "cyber security":           ["Linux","Python","Networking","Cyber Security","Ethical Hacking"],
    "java developer":           ["Java","Spring Boot","SQL","Git","GitHub"],
    "python developer":         ["Python","Django","Flask","SQL","Git","GitHub"],
    "web developer":            ["HTML","CSS","JavaScript","React","Node.js","Git"],
    "software engineer":        ["Python","Java","SQL","Git","GitHub"],
    "android developer":        ["Java","Kotlin","Android Studio","Firebase","Git"],
    "ios developer":            ["Swift","Xcode","Firebase","Git"],
    "ui ux designer":           ["Figma","UI/UX","Wireframing","Prototyping"],
    "qa engineer":              ["Manual Testing","Automation Testing","Selenium","Java","SQL"],
    "database administrator":   ["SQL","MySQL","PostgreSQL","MongoDB"],
    "network engineer":         ["Networking","Linux","Cisco","Routing","Switching"],
    "blockchain developer":     ["Solidity","Ethereum","Blockchain","Web3","JavaScript"],
    "game developer":           ["Unity","C#","Game Development","Blender"],
}

# SHORT/ALIAS names jo user type kar sakta hai → actual role key
ROLE_ALIASES = {
    # data
    "data science":         "data scientist",
    "data sci":             "data scientist",
    "ds":                   "data scientist",
    "data scientist":       "data scientist",
    "data analysis":        "data analyst",
    "data analytics":       "data analyst",
    "data analyst":         "data analyst",
    "da":                   "data analyst",
    # ml / ai
    "ml":                   "machine learning engineer",
    "machine learning":     "machine learning engineer",
    "ml engineer":          "machine learning engineer",
    "ai":                   "ai engineer",
    "ai engineer":          "ai engineer",
    # web
    "frontend":             "frontend developer",
    "front end":            "frontend developer",
    "front-end":            "frontend developer",
    "backend":              "backend developer",
    "back end":             "backend developer",
    "back-end":             "backend developer",
    "fullstack":            "full stack developer",
    "full stack":           "full stack developer",
    "full-stack":           "full stack developer",
    "web":                  "web developer",
    "web dev":              "web developer",
    # devops / cloud
    "devops":               "devops engineer",
    "cloud":                "cloud engineer",
    # mobile
    "android":              "android developer",
    "ios":                  "ios developer",
    "mobile":               "android developer",
    # others
    "cyber":                "cyber security",
    "security":             "cyber security",
    "hacking":              "cyber security",
    "ethical hacking":      "cyber security",
    "java":                 "java developer",
    "python":               "python developer",
    "software":             "software engineer",
    "swe":                  "software engineer",
    "ui":                   "ui ux designer",
    "ux":                   "ui ux designer",
    "ui ux":                "ui ux designer",
    "uiux":                 "ui ux designer",
    "design":               "ui ux designer",
    "qa":                   "qa engineer",
    "testing":              "qa engineer",
    "tester":               "qa engineer",
    "dba":                  "database administrator",
    "database":             "database administrator",
    "network":              "network engineer",
    "networking":           "network engineer",
    "blockchain":           "blockchain developer",
    "web3":                 "blockchain developer",
    "game":                 "game developer",
    "gaming":               "game developer",
}


SKILL_ALIASES = {
    "HTML":               [r"html"],
    "CSS":                [r"css"],
    "JavaScript":         [r"javascript", r"js"],
    "React":              [r"react", r"reactjs", r"react\.js"],
    "Angular":            [r"angular"],
    "Vue":                [r"vue"],
    "Bootstrap":          [r"bootstrap"],
    "Tailwind CSS":       [r"tailwind"],
    "Python":             [r"python"],
    "Java":               [r"java"],
    "Node.js":            [r"node", r"nodejs", r"node\.js"],
    "Django":             [r"django"],
    "Flask":              [r"flask"],
    "Spring Boot":        [r"spring boot"],
    "SQL":                [r"sql", r"mysql", r"postgresql", r"postgres", r"sqlite", r"sql server"],
    "MySQL":              [r"mysql"],
    "MongoDB":            [r"mongodb"],
    "PostgreSQL":         [r"postgresql"],
    "Power BI":           [r"power\s*bi", r"powerbi"],
    "Tableau":            [r"tableau"],
    "Machine Learning":   [r"machine\s+learning", r"\bml\b"],
    "Deep Learning":      [r"deep\s+learning", r"neural\s+network"],
    "NLP":                [r"\bnlp\b", r"natural\s+language\s+processing"],
    "Excel":              [r"excel", r"microsoft\s+excel"],
    "Data Analysis":      [r"data\s+anal", r"analytics"],
    "TensorFlow":         [r"tensorflow"],
    "PyTorch":            [r"pytorch"],
    "Linux":              [r"linux"],
    "Docker":             [r"docker"],
    "Kubernetes":         [r"kubernetes", r"k8s"],
    "AWS":                [r"aws", r"amazon web services"],
    "Azure":              [r"azure"],
    "CI/CD":              [r"ci/cd", r"ci cd"],
    "Jenkins":            [r"jenkins"],
    "Terraform":          [r"terraform"],
    "Kotlin":             [r"kotlin"],
    "Firebase":           [r"firebase"],
    "Swift":              [r"swift"],
    "Xcode":              [r"xcode"],
    "Android Studio":     [r"android studio"],
    "Figma":              [r"figma"],
    "UI/UX":              [r"ui/ux", r"ui ux", r"uiux"],
    "Wireframing":        [r"wireframing"],
    "Prototyping":        [r"prototyping"],
    "Selenium":           [r"selenium"],
    "Automation Testing": [r"automation testing"],
    "Manual Testing":     [r"manual testing"],
    "Networking":         [r"networking"],
    "Cyber Security":     [r"cyber security", r"cybersecurity"],
    "Ethical Hacking":    [r"ethical hacking"],
    "Cisco":              [r"cisco"],
    "Routing":            [r"routing"],
    "Switching":          [r"switching"],
    "Solidity":           [r"solidity"],
    "Ethereum":           [r"ethereum"],
    "Blockchain":         [r"blockchain"],
    "Web3":               [r"web3"],
    "Unity":              [r"unity"],
    "C#":                 [r"c#"],
    "Game Development":   [r"game development", r"game dev"],
    "Blender":            [r"blender"],
    "Git":                [r"\bgit\b"],
    "GitHub":             [r"github"],
}


def normalize_text(text: str) -> str:
    text = text or ""
    return re.sub(r"\s+", " ", text).strip()


# Generic stopwords — inhe description se keyword nikaalte waqt ignore karo
FREE_TEXT_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "of", "in", "on", "at", "to", "with",
    "is", "are", "was", "were", "be", "been", "being", "this", "that", "these",
    "those", "it", "as", "by", "from", "we", "you", "i", "he", "she", "they",
    "have", "has", "had", "do", "does", "did", "will", "would", "should",
    "can", "could", "may", "might", "must", "need", "not", "no", "yes", "if",
    "then", "than", "so", "such", "also", "etc", "looking", "candidate",
    "candidates", "required", "require", "requirement", "requirements",
    "years", "year", "job", "description", "role", "responsibilities",
    "skills", "skill", "please", "want", "wanted",
}


def extract_free_text_keywords(text: str) -> list[str]:
    """
    Description box mein jo bhi words type kiye hain unhe generic
    keywords ki tarah nikaalo — sirf predefined skill list tak limited
    nahi, taaki koi bhi term (SSC, HSC, college name, project, etc.)
    resumes mein search kiya ja sake.
    """
    normalized = normalize_text(text).lower()
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\+\.#/]*", normalized)
    seen: set[str] = set()
    keywords: list[str] = []
    for tok in tokens:
        if len(tok) < 2 or tok in FREE_TEXT_STOPWORDS or tok in seen:
            continue
        seen.add(tok)
        keywords.append(tok)
    return keywords


def keyword_search_in_text(resume_text: str, keywords: Iterable[str]) -> list[str]:
    """
    Description ke generic keywords ko resume ke pure text mein dhoondo
    (predefined skill list se independent — koi bhi word match ho sakta hai,
    jaise SSC, HSC, college name, ya koi bhi other term).
    """
    normalized = normalize_text(resume_text).lower()
    matched: list[str] = []
    for kw in keywords:
        kw_clean = (kw or "").strip().lower()
        if not kw_clean:
            continue
        if re.search(rf"(?<!\w){re.escape(kw_clean)}(?!\w)", normalized):
            matched.append(kw)
    return matched


def extract_skills(
    text: str,
    required_skills: Iterable[str] | None = None
) -> list[str]:
    normalized = normalize_text(text).lower()
    skills_to_check = list(required_skills or DEFAULT_SKILLS)
    found_skills = []
    for skill in skills_to_check:
        patterns = SKILL_ALIASES.get(skill, [re.escape(skill.lower())])
        if any(re.search(rf"(?<!\w){pattern}(?!\w)", normalized) for pattern in patterns):
            found_skills.append(skill)
    return sorted(set(found_skills), key=str.lower)


def extract_skills_from_job_description(job_description: str) -> list[str]:
    jd_lower = normalize_text(job_description).lower()
    detected_skills = []

    # 1. ALIAS matching — "data science", "ml", "frontend" etc.
    for alias, role_key in ROLE_ALIASES.items():
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", jd_lower):
            detected_skills.extend(ROLE_SKILLS.get(role_key, []))

    # 2. Full role name matching
    for role, skills in ROLE_SKILLS.items():
        role_words = role.split()
        if all(word in jd_lower for word in role_words):
            detected_skills.extend(skills)

    # 3. Direct skill keyword matching
    direct_skills = extract_skills(job_description, DEFAULT_SKILLS)
    detected_skills.extend(direct_skills)

    return list(set(detected_skills))


def get_missing_skills(
    found_skills: Iterable[str],
    required_skills: Iterable[str]
) -> list[str]:
    found_set = {skill.lower() for skill in found_skills}
    return [skill for skill in required_skills if skill.lower() not in found_set]


def create_resume_summary(text: str, max_sentences: int = 3) -> str:
    cleaned = normalize_text(text)
    if not cleaned:
        return "No readable text found."
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    summary = " ".join(sentences[:max_sentences])
    return summary or cleaned[:450]


def extract_experience_years(text: str) -> float:
    """
    Sirf WORK experience detect karo — education dates ignore karo.
    Detect: explicit 'X years experience' phrases + work date ranges only.
    Ignore: B.Tech/HSC/SSC/school/college dates, fresher resumes.
    """
    text_lower = normalize_text(text).lower()

    # Pattern 1: explicit "X years of experience" phrases only
    explicit_patterns = [
        r'(\d+\.?\d*)\s*\+?\s*years?\s+of\s+(?:work\s+)?experience',
        r'(\d+\.?\d*)\s*\+?\s*years?\s+(?:work\s+)?experience',
        r'experience\s+of\s+(\d+\.?\d*)\s*\+?\s*years?',
        r'(\d+\.?\d*)\s*\+?\s*yrs?\s+of\s+(?:work\s+)?experience',
        r'(\d+\.?\d*)\s*\+?\s*yrs?\s+(?:work\s+)?experience',
    ]
    years_found = []
    for pat in explicit_patterns:
        for m in re.findall(pat, text_lower):
            val = float(m)
            if 0 < val <= 40:
                years_found.append(val)
    if years_found:
        return round(max(years_found), 1)

    # Pattern 2: date ranges — only in lines WITHOUT education keywords
    edu_keywords = [
        'school', 'college', 'university', 'institute', 'b.tech', 'btech',
        'b.e', 'mtech', 'm.tech', 'hsc', 'ssc', '10th', '12th', 'diploma',
        'pursuing', 'bachelor', 'master', 'degree', 'graduation',
    ]
    work_context_keywords = [
        'internship', 'intern', 'worked', 'working', 'employed',
        'company', 'organization', 'job', 'role', 'position',
        'developer', 'engineer', 'analyst', 'manager', 'associate',
        'consultant', 'executive',
    ]

    lines = text_lower.split('\n')
    work_lines = [l for l in lines if not any(kw in l for kw in edu_keywords)]
    work_text = ' '.join(work_lines)

    if not any(kw in work_text for kw in work_context_keywords):
        return 0.0

    current_year = 2025
    date_ranges = re.findall(
        r'(20\d{2}|19\d{2})\s*[-\u2013to]+\s*(20\d{2}|19\d{2}|present|current|now)',
        work_text
    )
    total = 0.0
    for start, end in date_ranges:
        try:
            s = int(start)
            e = current_year if end in ("present", "current", "now") else int(end)
            diff = e - s
            if 0 < diff <= 15:
                total += diff
        except ValueError:
            pass
    return round(min(total, 40), 1)


def experience_label(years: float) -> str:
    """Human-readable experience label."""
    if years == 0:
        return "No experience mentioned"
    elif years < 1:
        return "Fresher / Intern"
    elif years < 3:
        return f"{years} yrs — Junior"
    elif years < 6:
        return f"{years} yrs — Mid-level"
    elif years < 10:
        return f"{years} yrs — Senior"
    else:
        return f"{years} yrs — Expert"


def extract_academic_marks(text: str) -> dict:
    """
    Resume text se 10th %, 12th % aur CGPA nikaalo.

    Returns:
        {
            "tenth": float | None,       # 10th percentage
            "twelfth": float | None,     # 12th percentage
            "cgpa": float | None,        # raw CGPA/GPA value
            "cgpa_scale": float,         # 10.0 or 4.0 — scale CGPA is on
        }
    """
    normalized = normalize_text(text).lower()

    def find_percent(patterns: list[str]) -> float | None:
        for pat in patterns:
            m = re.search(pat, normalized)
            if m:
                val = float(m.group(1))
                if 0 < val <= 100:
                    return val
        return None

    tenth_patterns = [
        r'10\s*th[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
        r'\bssc\b[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
        r'class\s*x[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
        r'matric(?:ulation)?[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
    ]
    twelfth_patterns = [
        r'12\s*th[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
        r'\bhsc\b[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
        r'class\s*xii[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
        r'intermediate[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
        r'senior\s+secondary[^\d]{0,25}(\d{1,3}(?:\.\d+)?)\s*%',
    ]

    tenth = find_percent(tenth_patterns)
    twelfth = find_percent(twelfth_patterns)

    cgpa = None
    cgpa_scale = 10.0

    # CGPA out of 10 — e.g. "CGPA: 8.5/10" or "CGPA 8.5"
    m = re.search(r'cgpa[^\d]{0,10}(\d{1,2}(?:\.\d+)?)\s*/\s*10', normalized)
    if not m:
        m = re.search(r'\bcgpa\b[^\d]{0,10}(\d{1,2}(?:\.\d+)?)(?!\s*/)', normalized)
    if m:
        val = float(m.group(1))
        if 0 < val <= 10:
            cgpa = val
            cgpa_scale = 10.0

    # GPA out of 4 — e.g. "GPA: 3.7/4"
    if cgpa is None:
        m = re.search(r'gpa[^\d]{0,10}(\d{1,2}(?:\.\d+)?)\s*/\s*4', normalized)
        if m:
            val = float(m.group(1))
            if 0 < val <= 4:
                cgpa = val
                cgpa_scale = 4.0

    return {
        "tenth": tenth,
        "twelfth": twelfth,
        "cgpa": cgpa,
        "cgpa_scale": cgpa_scale,
    }
