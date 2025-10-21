\
"""
Stub scraper for WAICY projects.
Later, you can implement actual scraping here (requests + BeautifulSoup) and
write results into data/waicy_projects_data.json in the same format as the sample.
For now, this script simply prints instructions.
"""
from pathlib import Path
import json

DATA = Path(__file__).parent / "data" / "waicy_projects_data.json"

def main():
    print("Scraper not implemented in this starter template.")
    print("When you are ready, replace the contents of", DATA, "with your scraped data.")
    print("Make sure it is a JSON array of objects with keys:")
    print("  project_name, year, category, summary, link")

if __name__ == "__main__":
    main()
