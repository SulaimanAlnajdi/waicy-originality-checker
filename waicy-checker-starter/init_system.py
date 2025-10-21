\
import os, sys, shutil, subprocess
from pathlib import Path

BASE = Path(__file__).parent
ENV = BASE / ".env"

def run(cmd):
    print(f"→ {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print("Command failed. Please copy this error and share it so we can help.")
        sys.exit(res.returncode)

def ensure_env():
    if ENV.exists():
        print("✓ .env already exists")
        return
    tmpl = BASE / ".env.template"
    if tmpl.exists():
        shutil.copy(tmpl, ENV)
        print("✓ Created .env from .env.template")
    else:
        ENV.write_text("ADMIN_PASSWORD=ChangeMe_2025!\nFLASK_SECRET_KEY=dev-secret-change-me\n", encoding="utf-8")
        print("✓ Created minimal .env")
    print("\nIMPORTANT: Open .env and set a strong ADMIN_PASSWORD.\n")

def main():
    print("="*70)
    print("WAICY Originality Checker — Windows Setup")
    print("="*70)

    # 1) Create virtual environment
    venv_dir = BASE / ".venv"
    if not venv_dir.exists():
        run("py -m venv .venv")
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")

    # 2) Activate instructions (can't activate from script in Windows CMD reliably)
    print("\nNext step (copy-paste in this window):")
    print(r""".venv\Scripts\activate""")
    input("\nPress Enter AFTER you activate the virtual environment...")

    # 3) Install packages
    if (BASE / "requirements.txt").exists():
        run("pip install -r requirements.txt")
    else:
        run("pip install flask flask-cors python-dotenv pandas openpyxl scikit-learn")

    print("✓ Dependencies installed")

    # 4) Ensure .env
    ensure_env()

    print("\nSetup finished!")
    print("To start the app now, run:")
    print("  py waicy_flask_app.py")
    print("\nThen open http://localhost:5000 in your browser.")

if __name__ == "__main__":
    main()
