# 🧠 AI Resume Analyzer

A clean, offline Resume Analyzer built using **Python (Flask)** for the backend and **HTML/CSS/JavaScript** for the frontend.  
It extracts text from resumes, detects skills accurately, evaluates resume quality, matches job roles, and visualizes results with interactive charts.

Perfect project to showcase full-stack + AI integration skills for internships.

---

## 🚀 Features

### 📝 Resume Text Extraction
- Supports **PDF, DOCX, TXT** files  
- Extracts and cleans text  
- Handles most normal resume formats  

### 🧠 Skill Detection
- Accurate skill matching using **word-boundary regex**  
- Avoids false positives (e.g., does *not* match “java” inside “javascript”)  
- Returns clean list of detected skills  

### 📊 Skill Strength & Resume Scoring
- Scores each skill (0–100) based on frequency  
- Generates an overall **resume score** (0–100)  
- Identifies strengths and weaknesses  

### 🎯 Job Role Matching
- Compares resume skills with pre-defined job-role keyword sets  
- Generates **match percentages** for each role  
- Shows **missing skills** for top recommended role  
- Suggests practical improvements  

### 💾 SQLite Storage
- Stores all resumes and their analysis  
- Fully offline, no paid APIs required  
- Automatically creates `resumes.db`  

### 🖥️ Clean Frontend UI
- Responsive design  
- File upload form  
- Result summary + bar chart visualization  
- JSON output link for developers  

---

## 🧩 Project Structure

ai-resume-analyzer/
├─ backend/
│ ├─ app.py # Flask API
│ ├─ database.py # SQLite DB helpers
│ ├─ extract.py # Text extraction + skill detection
│ ├─ skills_db.py # Skills + job roles dictionary
│ ├─ uploads/ # Uploaded resumes (auto-created)
│ ├─ resumes.db # SQLite DB (auto-created)
│ └─ requirements.txt # Python dependencies
├─ frontend/
│ ├─ index.html
│ ├─ styles.css
│ └─ script.js
└─ README.md


---

## 🛠️ Installation & Running Locally

### 1️⃣ Clone or open the project in VS Code  
```bash
cd ai-resume-analyzer

2️⃣ Set up Python environment
cd backend
python -m venv venv

3️⃣ Activate virtual environment
Windows (PowerShell):
.\venv\Scripts\Activate.ps1

Mac/Linux:
source venv/bin/activate

4️⃣ Install required packages
pip install -r requirements.txt

5️⃣ Reset database (optional, for fresh start)
# Windows
del .\resumes.db

# Mac/Linux
rm ./resumes.db

6️⃣ Start the Flask server
python app.py

7️⃣ Open frontend
Go to:
http://127.0.0.1:5000
Upload a resume → analyze → view results.