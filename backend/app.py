import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path

from database import init_db, save_resume, save_analysis
from extract import (
    extract_text,
    extract_skills_from_text,
    score_skill_strengths,
    score_resume,
    match_jobs,
    suggest_missing,
)

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXT = {".pdf", ".docx", ".doc", ".txt"}

app = Flask(__name__, static_folder=str(Path(__file__).parent.parent / "frontend"), static_url_path="/")
CORS(app)

# initialize DB (creates file/tables if missing)
init_db()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/upload-resume", methods=["POST"])
def upload_resume():
    # Basic validations
    if "resume" not in request.files:
        return jsonify({"error": "no file"}), 400
    f = request.files["resume"]
    filename = secure_filename(f.filename)
    if not filename:
        return jsonify({"error": "empty filename"}), 400
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": "file type not allowed, use PDF/DOCX/TXT"}), 400

    # Save file
    save_path = UPLOAD_DIR / filename
    try:
        f.save(save_path)
    except Exception as e:
        return jsonify({"error": f"failed to save file: {e}"}), 500

    # Extract text
    try:
        text = extract_text(str(save_path), filename)
    except Exception as e:
        return jsonify({"error": f"failed to extract text: {e}"}), 500

    # Process
    try:
        skills = extract_skills_from_text(text)
        skill_strengths = score_skill_strengths(text, skills)
        score = score_resume(skills, text)
        matches = match_jobs(skills)
    except Exception as e:
        return jsonify({"error": f"processing error: {e}"}), 500

    # safe top role fallback
    top_role = max(matches.items(), key=lambda x: x[1])[0] if matches else None
    missing = suggest_missing(skills, top_role) if top_role else []

    suggestions = f"Top role: {top_role}. Missing: {missing}. Improve measurable achievements."

    # Save to DB
    try:
        resume_id = save_resume(filename, text)
        save_analysis(resume_id, skills, missing, score, matches, suggestions)
    except Exception as e:
        return jsonify({"error": f"database error: {e}"}), 500

    return jsonify(
        {
            "resume_id": resume_id,
            "filename": filename,
            "skills": skills,
            "skill_strengths": skill_strengths,
            "missing_skills": missing,
            "resume_score": score,
            "match_scores": matches,
            "suggestions": suggestions,
        }
    )


@app.route("/api/results/<int:resume_id>", methods=["GET"])
def get_results(resume_id):
    import sqlite3, json

    db_path = Path(__file__).parent / "resumes.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Fetch resume info
    cur.execute("SELECT id, filename, uploaded_at, extracted_text FROM resumes WHERE id=?", (resume_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Resume not found"}), 404

    resume_data = {"id": row[0], "filename": row[1], "uploaded_at": row[2], "extracted_text": row[3]}

    # Fetch analysis record
    cur.execute(
        "SELECT skills, missing_skills, resume_score, match_scores, suggestions, created_at "
        "FROM analysis WHERE resume_id=? ORDER BY created_at DESC LIMIT 1",
        (resume_id,),
    )
    arow = cur.fetchone()
    conn.close()

    if not arow:
        return jsonify({"error": "Analysis not found"}), 404

    analysis_data = {
        "skills": json.loads(arow[0]),
        "missing_skills": json.loads(arow[1]),
        "resume_score": arow[2],
        "match_scores": json.loads(arow[3]),
        "suggestions": arow[4],
        "created_at": arow[5],
    }

    return jsonify({"resume": resume_data, "analysis": analysis_data})


# Static proxy (placed after API routes so APIs resolve first)
@app.route("/<path:path>")
def static_proxy(path):
    # Prevent serving frontend HTML for API routes
    if path.startswith("api/") or path.startswith("api"):
        return jsonify({"error": "not found"}), 404
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
