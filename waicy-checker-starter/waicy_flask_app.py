\
import os, json, io, hashlib
from pathlib import Path
from flask import Flask, request, jsonify, session, send_file, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import csv

# Simple, offline similarity using TF-IDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "waicy_projects_data.json"
LOG_CSV = BASE_DIR / "data" / "submissions_log.csv"   # append-only

load_dotenv(BASE_DIR / ".env")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or "ChangeMe_2025!"
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or "dev-secret-change-me"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = FLASK_SECRET_KEY
CORS(app)

# -------------------- Helpers --------------------

def require_auth():
    if not session.get("logged_in"):
        return False
    return True

def load_projects():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def tfidf_similarity(query, projects, top_k=10):
    texts = [p.get("summary", "") + " " + p.get("project_name", "") for p in projects]
    if not texts:
        return []
    vectorizer = TfidfVectorizer(stop_words="english")
    mat = vectorizer.fit_transform(texts + [query])
    sims = cosine_similarity(mat[-1], mat[:-1]).flatten()
    # Attach scores and sort
    scored = []
    for i, p in enumerate(projects):
        scored.append({**p, "score": float(sims[i])})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def verdict_for(score):
    if score >= 0.6:
        return "Very similar"
    if score >= 0.35:
        return "Somewhat similar"
    return "Likely unique"

def suggestions_for(top_score):
    if top_score < 0.35:
        return []
    return [
        "Narrow the target users (e.g., a specific age group or context).",
        "Change the data source or sensing method (e.g., audio instead of images).",
        "Add a novel feature that past projects lacked (e.g., personalization, explainability).",
        "Focus on measurable impact with a unique evaluation metric."
    ]

# -------------------- Routes --------------------

@app.route("/")
def home():
    # If already logged in, show app directly
    return render_template("index.html")

@app.post("/login")
def login():
    body = request.get_json(force=True, silent=True) or {}
    password = (body.get("password") or "").strip()
    if not password:
        return jsonify({"error": "Password required"}), 400
    # Compare raw (for demo). For production, hash and compare stored hash.
    if password == ADMIN_PASSWORD:
        session["logged_in"] = True
        return jsonify({"ok": True})
    return jsonify({"error": "Unauthorized"}), 401

@app.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.get("/api/projects")
def api_projects():
    #if not require_auth():
    #    return jsonify({"error": "Unauthorized"}), 401
    projects = load_projects()
    return jsonify({"projects": projects})

@app.post("/api/check")
@app.post("/api/check_and_log")
def api_check_and_log():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    grade = (data.get("grade") or "").strip()
    track = (data.get("track") or "").strip()
    idea = (data.get("idea") or "").strip()
    if not (name and grade and track and idea):
        return jsonify({"error": "name, grade, track, idea are required"}), 400

    # same logic as /api/check
    projects = load_projects()
    if not projects:
        return jsonify({"error": "No projects loaded yet."}), 500

    ranked = tfidf_similarity(idea, projects, top_k=5)
    top_score = ranked[0]["score"] if ranked else 0.0

    if top_score >= 0.6:
        verdict = "Your idea is very similar to some past projects."
        message = "Consider making substantial changes to scope, data, or methods."
    elif top_score >= 0.35:
        verdict = "Your idea is somewhat similar to past projects."
        message = "You can differentiate with a narrower focus or a unique feature."
    else:
        verdict = "Your idea appears unique among the loaded projects."
        message = "Great start! Keep refining the problem statement and evaluation plan."

    # append to CSV log
    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    is_new = not LOG_CSV.exists()
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow([
                "timestamp","name","grade","track","idea",
                "verdict","top_score","top_match_names"
            ])
        top_names = "; ".join([m.get("project_name","") for m in ranked])
        writer.writerow([
            datetime.utcnow().isoformat(),
            name, grade, track, idea, verdict, f"{top_score:.4f}", top_names
        ])

    return jsonify({
        "verdict": verdict,
        "message": message,
        "matches": ranked,
        "suggestions": suggestions_for(top_score)
    })

def api_check():
    if not require_auth():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True, silent=True) or {}
    idea = (data.get("idea") or "").strip()
    if not idea:
        return jsonify({"error": "Please provide 'idea' text"}), 400

    projects = load_projects()
    if not projects:
        return jsonify({"verdict": "No data", "message": "No projects loaded yet.", "matches": []})

    ranked = tfidf_similarity(idea, projects, top_k=5)
    top_score = ranked[0]["score"] if ranked else 0.0

    # Determine overall verdict/message
    if top_score >= 0.6:
        verdict = "Your idea is very similar to some past projects."
        message = "Consider making substantial changes to scope, data, or methods."
    elif top_score >= 0.35:
        verdict = "Your idea is somewhat similar to past projects."
        message = "You can differentiate with a narrower focus or a unique feature."
    else:
        verdict = "Your idea appears unique among the loaded projects."
        message = "Great start! Keep refining the problem statement and evaluation plan."

    return jsonify({
        "verdict": verdict,
        "message": message,
        "matches": ranked,
        "suggestions": suggestions_for(top_score)
    })

@app.get("/download_excel")
def download_excel():
    if not require_auth():
        return jsonify({"error": "Unauthorized"}), 401
    projects = load_projects()
    if not projects:
        return jsonify({"error": "No data"}), 404
    df = pd.DataFrame(projects, columns=["project_name", "year", "category", "summary", "link"])
    df = df.rename(columns={
        "project_name": "Project Name",
        "year": "Year",
        "category": "Category / Medal",
        "summary": "Short Summary",
        "link": "Project Link"
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="WAICY Projects")
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="waicy_projects.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/admin")
def admin_home():
    if not session.get("logged_in"):
        return """
        <html><body style="font-family:Arial;padding:24px;">
          <h3>Admin Login</h3>
          <form method="post" action="/login_admin">
            <input type="password" name="password" placeholder="Admin password" />
            <button type="submit">Login</button>
          </form>
          <p><a href="/">Back</a></p>
        </body></html>
        """
    return """
    <html><body style="font-family:Arial;padding:24px;">
      <h3>Admin</h3>
      <ul>
        <li><a href="/download_excel">Download Projects Excel</a></li>
        <li><a href="/admin/download_submissions_excel">Download Submissions Excel</a></li>
        <li><form method="post" action="/logout"><button>Logout</button></form></li>
      </ul>
      <p><a href="/">Back</a></p>
    </body></html>
    """

@app.post("/login_admin")
def login_admin():
    password = (request.form.get("password") or "").strip()
    if password == ADMIN_PASSWORD:
        session["logged_in"] = True
        return ("<script>location.href='/admin'</script>", 200)
    return ("<script>alert('Wrong password');history.back()</script>", 401)

@app.get("/admin/download_submissions_excel")
def admin_download_submissions_excel():
    if not session.get("logged_in"):
        return jsonify({"error":"Unauthorized"}), 401
    if not LOG_CSV.exists():
        return jsonify({"error":"No submissions yet"}), 404
    df = pd.read_csv(LOG_CSV)
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Submissions")
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="waicy_submissions.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)