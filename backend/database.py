# backend/database.py
import sqlite3
from datetime import datetime
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "resumes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create resumes table (NO user_id)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
      id INTEGER PRIMARY KEY,
      filename TEXT,
      uploaded_at TEXT,
      extracted_text TEXT
    )
    ''')

    # Create analysis table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS analysis (
      id INTEGER PRIMARY KEY,
      resume_id INTEGER,
      skills TEXT,
      missing_skills TEXT,
      resume_score INTEGER,
      match_scores TEXT,
      suggestions TEXT,
      created_at TEXT,
      FOREIGN KEY(resume_id) REFERENCES resumes(id)
    )
    ''')

    conn.commit()
    conn.close()


def save_resume(filename, text):
    """Save a resume (simple version, no user_id)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    uploaded_at = datetime.utcnow().isoformat()

    cur.execute(
        'INSERT INTO resumes (filename, uploaded_at, extracted_text) VALUES (?, ?, ?)',
        (filename, uploaded_at, text)
    )

    resume_id = cur.lastrowid
    conn.commit()
    conn.close()
    return resume_id


def save_analysis(resume_id, skills, missing_skills, resume_score, match_scores, suggestions):
    """Save analysis results into the DB."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
      INSERT INTO analysis (resume_id, skills, missing_skills, resume_score, match_scores, suggestions, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        json.dumps(skills),
        json.dumps(missing_skills),
        int(resume_score),
        json.dumps(match_scores),
        suggestions,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()