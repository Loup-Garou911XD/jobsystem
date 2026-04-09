import requests
from config import APIFY_TOKEN, INDEED_API_URL, DEFAULT_LOCATION, DEFAULT_JOB_LIMIT
from database.models import insert_job

def scrape_indeed(position="web developer", location=DEFAULT_LOCATION, limit=DEFAULT_JOB_LIMIT):
    """
    Calls the Apify Indeed Scraper API and saves jobs to the database.
    """
    print(f"Scraping Indeed for {position} in {location}...")
    
    url = f"{INDEED_API_URL}?token={APIFY_TOKEN}"
    payload = {
        "country": "US",
        "followApplyRedirects": False,
        "location": location,
        "maxItemsPerSearch": limit,
        "parseCompanyDetails": False,
        "position": position,
        "saveOnlyUniqueItems": True
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Apify acts run-sync-get-dataset-items returns a list of items directly
        if not isinstance(data, list):
            print("Unexpected indeed payload format:", data)
            return
            
        inserted_count = 0
        for item in data:
            title = item.get("positionName") or item.get("title") or "Unknown"
            company = item.get("company") or "Unknown"
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
                source="Indeed"
            )
            inserted_count += 1
            
        print(f"Indeed: Inserted {inserted_count} jobs.")
        
    except Exception as e:
        print(f"Error scraping Indeed: {e}")

if __name__ == '__main__':
    from database.db import init_db
    init_db()
    scrape_indeed()
