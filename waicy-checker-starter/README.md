# WAICY Originality Checker — Starter (Windows friendly)

## Quick Start (Windows)

1. **Extract** this folder somewhere easy (e.g., `C:\Users\YourName\waicy-checker`).
2. Open **Command Prompt** inside the folder:
   - Click the folder path bar, type `cmd`, press Enter.
3. Run the setup script:
   ```bat
   py init_system.py
   ```
   - When it pauses, copy-paste:
     ```bat
     .venv\Scripts\activate
     ```
   - Press **Enter** to continue, then it installs packages and creates `.env`.
4. Edit the `.env` file and change `ADMIN_PASSWORD` to your password.
5. Start the website:
   ```bat
   py waicy_flask_app.py
   ```
6. Open your browser at **http://localhost:5000** and log in with your password.
7. (Optional) Export Excel via the link at the top-right of the page.

### Later: add real data
- Replace `data/waicy_projects_data.json` with your own JSON in the same format.
- Or implement the scraper in `waicy_scraper.py`.
