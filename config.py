import os

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'jobs_data', 'jobs.db')

# Apify APIs
APIFY_TOKEN = 'apify_api_3eK6bbgWWJ5xkzJgqWd6m40acJ5GMY19iQXi'

# Scraper configurations
INDEED_API_URL = 'https://api.apify.com/v2/acts/misceres~indeed-scraper/run-sync-get-dataset-items'
LINKEDIN_API_URL = (
    'https://api.apify.com/v2/acts/curious_coder~linkedin-jobs-scraper/run-sync-get-dataset-items'
)

# Scraping settings
DEFAULT_LOCATION = 'San Francisco'
DEFAULT_JOB_LIMIT = 50
