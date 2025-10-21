\
import json
from pathlib import Path

# Basic sanity checks for starter bundle
ROOT = Path(__file__).parent
assert (ROOT / "waicy_flask_app.py").exists(), "Missing waicy_flask_app.py"
assert (ROOT / "init_system.py").exists(), "Missing init_system.py"
assert (ROOT / "requirements.txt").exists(), "Missing requirements.txt"
assert (ROOT / "templates" / "index.html").exists(), "Missing templates/index.html"
assert (ROOT / "data" / "waicy_projects_data.json").exists(), "Missing sample data"

# Validate sample data format
data = json.loads((ROOT / "data" / "waicy_projects_data.json").read_text(encoding="utf-8"))
assert isinstance(data, list) and len(data) >= 1, "Sample data should be a non-empty list"
for item in data:
    for key in ["project_name", "year", "summary"]:
        assert key in item, f"Missing '{key}' in data item"

print("All starter checks passed ✔")
