# TheWatch/core/config.py
from pydantic_settings import BaseSettings

# Algolia credentials from the Grailed website
ALGOLIA_APP_ID = "MNRWEFSS2Q"
ALGOLIA_API_KEY = "bc9ee1c014521ccf312525a4ef324a16"
ALGOLIA_INDEX = "Listing_sold_production"

# Base URLs
BASE_URL = "https://www.grailed.com"
API_BASE_URL = f"{BASE_URL}/api"
ALGOLIA_BASE_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes"

# API endpoints
ENDPOINTS = {
    "listings": "/listings/grid",
    "listing_details": "/listings/{id}",
}

# Rate limiting settings
RATE_LIMIT_REQUESTS = 50  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds, will be multiplied by attempt number for backoff

# Default headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.grailed.com/shop',
    'Origin': 'https://www.grailed.com'
}

# Search settings
DEFAULT_PAGE_SIZE = 40
DEFAULT_MAX_PAGES = 3
DEFAULT_SORT = "sold_date_desc"

# Condition mappings
CONDITION_MAP = {
    "is_new": "New",
    "is_gently_used": "Gently Used",
    "is_used": "Used",
    "is_very_worn": "Very Worn"
}


class Settings(BaseSettings):
    """Application settings"""
    # Algolia settings
    algolia_app_id: str = ALGOLIA_APP_ID
    algolia_api_key: str = ALGOLIA_API_KEY
    algolia_index: str = ALGOLIA_INDEX
    algolia_base_url: str = ALGOLIA_BASE_URL  # Added this line

    # Base URLs
    base_url: str = BASE_URL
    api_base_url: str = API_BASE_URL

    # Rate limiting
    rate_limit_requests: int = RATE_LIMIT_REQUESTS
    rate_limit_window: int = RATE_LIMIT_WINDOW

    # Request settings
    request_timeout: int = REQUEST_TIMEOUT
    max_retries: int = MAX_RETRIES
    retry_delay: int = RETRY_DELAY

    # Search settings
    default_page_size: int = DEFAULT_PAGE_SIZE
    default_max_pages: int = DEFAULT_MAX_PAGES
    default_sort: str = DEFAULT_SORT

    class Config:
        env_prefix = "GRAILED_"


# Create settings instance
settings = Settings()

# Export settings
__all__ = [
    'ALGOLIA_APP_ID',
    'ALGOLIA_API_KEY',
    'ALGOLIA_INDEX',
    'ALGOLIA_BASE_URL',
    'BASE_URL',
    'API_BASE_URL',
    'ENDPOINTS',
    'DEFAULT_HEADERS',
    'CONDITION_MAP',
    'settings'
]