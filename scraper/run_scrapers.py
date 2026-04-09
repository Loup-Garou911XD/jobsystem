import sys
import os
import time

# Add parent to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.indeed_scraper import scrape_indeed
from scraper.linkedin_scraper import scrape_linkedin
from scraper.naukri_scraper import scrape_naukri
from database.db import init_db


def run_all_scrapers(position="web developer", location="Jaipur", limit=50):
    print(f"--- Starting scraping job for {position} located in {location} ---")
    # scrape_indeed(position=position, location=location, limit=limit)
    # scrape_linkedin(position=position, location=location, limit=limit)
    scrape_naukri(position=position, location=location, limit=limit)
    print("--- Scraping job completed ---")


if __name__ == '__main__':
    # Initialize the DB first
    init_db()

    # Normally you'd want this script to be scheduled via cron or a task scheduler (e.g. APScheduler / schedule)
    # For now, it just runs once when executed.

    positions = ["web developer", "python developer", "data scientist"]
    # You can loop through positions or execute specific ones
    for pos in positions:
        run_all_scrapers(position=pos, location="San Francisco", limit=30)
        time.sleep(2)  # avoid spamming Apify continuously
