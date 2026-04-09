import requests
import urllib.parse
from config import APIFY_TOKEN, LINKEDIN_API_URL, DEFAULT_LOCATION, DEFAULT_JOB_LIMIT
from database.models import insert_job

def scrape_linkedin(position="web developer", location=DEFAULT_LOCATION, limit=DEFAULT_JOB_LIMIT):
    """
    Calls the Apify LinkedIn Jobs Scraper API and saves jobs to the database.
    """
    print(f"Scraping LinkedIn for {position} in {location}...")
    
    url = f"{LINKEDIN_API_URL}?token={APIFY_TOKEN}"
    
    # URL encode keywords
    query_pos = urllib.parse.quote(position)
    query_loc = urllib.parse.quote(location)
    li_url = f"https://www.linkedin.com/jobs/search/?keywords={query_pos}&location={query_loc}"
    
    payload = {
        "count": limit,
        "scrapeCompany": False,
        "splitByLocation": False,
        "urls": [li_url]
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, list):
            print("Unexpected linkedin payload format:", data)
            return
            
        inserted_count = 0
        for item in data:
            title = item.get("title") or "Unknown"
            company = item.get("companyName") or item.get("company") or "Unknown"
            loc = item.get("location") or location
            desc = item.get("description") or "No description available."
            job_url = item.get("url") or item.get("jobUrl") or ""
            
            if not job_url:
                continue
                
            insert_job(
                title=title,
                company=company,
                location=loc,
                description=desc,
                url=job_url,
                source="LinkedIn"
            )
            inserted_count += 1
            
        print(f"LinkedIn: Inserted {inserted_count} jobs.")
        
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")

if __name__ == '__main__':
    from database.db import init_db
    init_db()
    scrape_linkedin()
