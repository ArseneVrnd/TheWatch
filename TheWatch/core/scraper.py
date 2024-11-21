import aiohttp
import asyncio
from typing import List, Dict, Optional, Any, Tuple
import logging
import json
import time
from datetime import datetime
from collections import deque
from bs4 import BeautifulSoup
import re
import urllib.parse
from .models import Sale, SearchFilters

logger = logging.getLogger(__name__)


class GrailedScraper:
    def __init__(self):
        self.base_url = "https://www.grailed.com"
        self.session = None
        self.last_request_time = 0
        self.min_request_interval = 1.0
        self.request_history = deque(maxlen=10)
        self.rate_limit_window = 60
        self.max_requests = 10

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.grailed.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }

    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

            # Get initial page to set up cookies
            try:
                headers = {
                    **self.headers,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
                }
                async with self.session.get(self.base_url, headers=headers) as response:
                    await response.text()
            except Exception as e:
                logger.error(f"Error initializing session: {e}")

    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[Any]:
        if not self.session:
            await self._init_session()

        try:
            async with getattr(self.session, method.lower())(url, **kwargs) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return None

                response.raise_for_status()

                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    return await response.json()
                return await response.text()

        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return None

    async def _get_custom_search_url(self, query: str) -> Optional[str]:
        """Get the custom search URL by observing network requests"""
        try:
            # Make initial search request
            search_url = f"{self.base_url}/shop/{query.replace(' ', '+')}"
            html = await self._make_request(search_url)

            if not html:
                return None

            # Look for redirect URL in the HTML
            soup = BeautifulSoup(html, 'html.parser')

            # Try finding redirect meta tag
            meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
            if meta_refresh:
                content = meta_refresh.get('content', '')
                match = re.search(r'url=(.+?)(?:;|$)', content)
                if match:
                    return match.group(1)

            # Try finding canonical link
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            if canonical and canonical.get('href'):
                return canonical['href']

            # Look for the URL in Next.js data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and '"query":' in script.string:
                    try:
                        data = json.loads(script.string)
                        if 'props' in data and 'pageProps' in data['props']:
                            custom_url = data['props']['pageProps'].get('canonicalUrl')
                            if custom_url:
                                return f"{self.base_url}{custom_url}"
                    except json.JSONDecodeError:
                        continue

            logger.warning(f"Could not find custom URL, using original: {search_url}")
            return search_url

        except Exception as e:
            logger.error(f"Error getting custom search URL: {str(e)}")
            return None

    async def _get_listings_data(self, url: str, page: int = 1) -> List[Dict]:
        """Get listings data from API"""
        try:
            # Extract path part for API request
            path = url.split('www.grailed.com/')[-1]
            api_url = f"{self.base_url}/api/{path}/goods"

            params = {
                "page": page,
                "per_page": 40,
                "sort": "default"
            }

            data = await self._make_request(api_url, params=params)
            if not data:
                return []

            return data.get('listings', [])

        except Exception as e:
            logger.error(f"Error getting listings data: {str(e)}")
            return []

    def _process_listing(self, data: Dict) -> Optional[Sale]:
        try:
            original_price = float(data.get('original_price', 0) or data.get('price', 0))
            price = float(data.get('price', 0))

            discount = original_price - price if original_price > price else None
            discount_percentage = (discount / original_price * 100) if discount else None

            return Sale(
                id=data.get('id'),
                title=data.get('title', '').strip(),
                price=price,
                original_price=original_price,
                designer=' × '.join(data.get('designer_names', ['Unknown'])),
                size=data.get('size', 'Unknown'),
                condition=data.get('condition', 'Unknown'),
                location=data.get('location', 'Unknown'),
                seller=data.get('seller', {}).get('username', 'Unknown'),
                url=f"https://www.grailed.com/listings/{data.get('id')}",
                photos=[p.get('url') for p in data.get('photos', []) if p.get('url')],
                created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                category=data.get('category', 'Unknown'),
                description=data.get('description', '').strip(),
                discount=discount,
                discount_percentage=discount_percentage
            )
        except Exception as e:
            logger.error(f"Error processing listing: {str(e)}")
            return None

    async def search_listings(
            self,
            query: str,
            filters: Optional[SearchFilters] = None,
            page: int = 1
    ) -> List[Sale]:
        try:
            # First get the custom search URL
            logger.info(f"Getting custom search URL for query: {query}")
            custom_url = await self._get_custom_search_url(query)

            if not custom_url:
                logger.error("Failed to get custom search URL")
                return []

            logger.info(f"Using custom URL: {custom_url}")

            # Get listings using the custom URL
            raw_listings = await self._get_listings_data(custom_url, page)

            # Process listings
            listings = []
            for raw_listing in raw_listings:
                listing = self._process_listing(raw_listing)
                if listing:
                    listings.append(listing)

            return listings

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None