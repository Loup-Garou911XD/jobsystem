import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from config import DEFAULT_LOCATION, DEFAULT_JOB_LIMIT
from database.models import insert_job
import time


def scrape_naukri(position="web developer", location=DEFAULT_LOCATION, limit=DEFAULT_JOB_LIMIT):
    """
    Scrapes Naukri.com directly from the web using Selenium and saves jobs to the database.
    """
    print(f"Scraping Naukri for {position} in {location}...")

    # Format for URL (replace spaces with hyphens)
    position_url = position.replace(" ", "-").lower()
    location_url = location.replace(" ", "-").lower()

    base_url = f"https://www.naukri.com/{position_url}-jobs-in-{location_url}"

    # Setup Firefox options
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run in headless mode
    firefox_options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    )

    driver = None
    try:
        driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()), options=firefox_options
        )

        # Add query parameters
        url_with_params = f"{base_url}?k={position}&l={location}"
        print(f"Fetching: {url_with_params}")
        driver.get(url_with_params)

        # Wait for job listings to load
        time.sleep(3)  # Give page time to render

        # Try to wait for job cards to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "article.jobTuple, div[data-job-id]")
                )
            )
        except:
            print("Timeout waiting for job cards, continuing with current page...")

        # Get the rendered HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find job listings with the correct selector
        job_cards = soup.find_all("div", class_="srp-jobtuple-wrapper")

        print(f"Found {len(job_cards)} job listings")

        inserted_count = 0
        for job_card in job_cards[:limit]:
            try:
                # Extract job title
                title_elem = job_card.find("a", class_="title")
                title = title_elem.get_text(strip=True) if title_elem else "Unknown"

                # Extract company name
                company_elem = job_card.find("a", class_="comp-name")
                company = company_elem.get_text(strip=True) if company_elem else "Unknown"

                # Extract job URL
                job_url = title_elem.get("href", "") if title_elem else ""

                # Extract job location - look for location info in the card
                # Naukri may have location in title or separate element
                loc_parts = job_card.get_text(strip=True).split()
                loc = location  # Default to search location

                # Extract job description/summary
                desc_elem = job_card.find("div", class_="job-desc")
                if not desc_elem:
                    desc_elem = job_card.find(class_="ni-job-tuple")
                desc = (
                    desc_elem.get_text(strip=True)[:300]
                    if desc_elem
                    else job_card.get_text(strip=True)[:300]
                )

                if not job_url or title == "Unknown":
                    continue

                insert_job(
                    title=title,
                    company=company,
                    location=loc,
                    description=desc,
                    url=job_url,
                    source="Naukri",
                )
                inserted_count += 1

            except Exception as item_error:
                print(f"Error parsing individual job: {item_error}")
                continue

        print(f"Naukri: Inserted {inserted_count} jobs.")

    except Exception as e:
        print(f"Error scraping Naukri: {e}")

    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    from database.db import init_db

    init_db()
    scrape_naukri()
