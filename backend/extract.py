# backend/extract.py
import pdfplumber
import docx
import re
from skills_db import COMMON_SKILLS, JOB_ROLES   # use COMMON_SKILLS from skills_db

def extract_text_from_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            text.append(t)
    return "\n".join(text)

def extract_text_from_docx(path):
    doc = docx.Document(path)
    texts = [p.text for p in doc.paragraphs]
    return "\n".join(texts)

def extract_text(path, filename):
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif filename.lower().endswith(".docx") or filename.lower().endswith(".doc"):
        return extract_text_from_docx(path)
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def normalize_text(t):
    t = t.lower()
    t = re.sub(r'[\r\n]+', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t

# Return a list of skills found (strings)
def extract_skills_from_text(text):
    """
    Extract skills with exact matching:
    - normalizes text (removes newlines/punctuation spacing)
    - avoids matching 'java' inside 'javascript'
    - uses word boundaries
    - checks longer skill names first (javascript -> java)
    """
    text_norm = normalize_text(text)

    # sort by length desc so longer terms match before substrings
    skills_sorted = sorted(COMMON_SKILLS, key=lambda x: -len(x))
    found = []

    for skill in skills_sorted:
        skill_l = skill.lower().strip()
        # escape regex and match whole word/phrase
        # use \b for alphanumeric skills, otherwise use non-word boundaries
        esc = re.escape(skill_l)
        if re.match(r'^[a-z0-9 ]+$', skill_l):
            pattern = r'\b' + esc + r'\b'
        else:
            pattern = r'(?<!\w)' + esc + r'(?!\w)'

        if re.search(pattern, text_norm):
            found.append(skill_l)

    # return unique sorted list (alphabetical)
    return sorted(set(found))


# New: produce a numeric strength (0-100) per detected skill
def score_skill_strengths(text, skills):
    """
    Count occurrences using word-boundary regex for each detected skill,
    and map frequency -> heuristic score (0-100).
    """
    text_norm = normalize_text(text)
    strengths = {}

    for skill in skills:
        skill_l = skill.lower().strip()
        esc = re.escape(skill_l)
        if re.match(r'^[a-z0-9 ]+$', skill_l):
            pattern = r'\b' + esc + r'\b'
        else:
            pattern = r'(?<!\w)' + esc + r'(?!\w)'

        matches = re.findall(pattern, text_norm)
        count = len(matches)

        # heuristic mapping frequency -> score (0-100)
        if count == 0:
            score = 0
        elif count == 1:
            score = 60
        elif count == 2:
            score = 75
        elif count >= 3:
            score = 90
        else:
            score = 50

        strengths[skill_l] = score

    return strengths

def match_jobs(skills_found):
    results = {}
    for role, keywords in JOB_ROLES.items():
        overlap = 0
        for kw in keywords:
            if kw in skills_found:
                overlap += 1
        if len(keywords) == 0:
            s = 0
        else:
            s = int((overlap / len(keywords)) * 100)
        results[role] = s
    return results

def suggest_missing(skills_found, target_role):
    keywords = JOB_ROLES.get(target_role, [])
    missing = [k for k in keywords if k not in skills_found]
    return missing
