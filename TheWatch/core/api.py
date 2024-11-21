# thewatch/core/api.py
from dataclasses import dataclass

import aiohttp
import asyncio
from typing import List, Dict, Optional, Any
import logging
from bs4 import BeautifulSoup
import json
from datetime import datetime
from TheWatch.core.models import Sale, SearchFilters

logger = logging.getLogger(__name__)


class GrailedAPI:
    def __init__(self):
        self.base_url = "https://www.grailed.com"
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.grailed.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }

    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
            try:
                headers = {**self.headers, 'Accept': 'text/html,application/xhtml+xml'}
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

    async def get_search_url(self, query: str) -> Optional[str]:
        search_url = f"{self.base_url}/shop/{query.replace(' ', '+')}"
        html = await self._make_request(search_url)

        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script', type='application/json')

        for script in scripts:
            try:
                data = json.loads(script.string)
                if 'props' in data and 'pageProps' in data['props']:
                    custom_url = data['props']['pageProps'].get('canonicalUrl')
                    if custom_url:
                        return f"{self.base_url}{custom_url}"
            except:
                continue

        return search_url

    async def get_listings(self, url: str, page: int = 1) -> List[Dict]:
        try:
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
            logger.error(f"Error getting listings: {str(e)}")
            return []

    def process_listing(self, listing: Dict) -> Optional[Sale]:
        try:
            price = float(listing.get('price', 0))
            original_price = float(listing.get('original_price', 0) or price)

            return Sale(
                title=listing.get('title', '').strip(),
                price=price,
                original_price=original_price,
                sold_date=datetime.fromisoformat(listing.get('sold_date', datetime.now().isoformat())),
                designer=listing.get('designer_names', ['Unknown'])[0],
                size=listing.get('size', 'Unknown'),
                condition=listing.get('condition', 'Unknown'),
                url=f"https://www.grailed.com/listings/{listing.get('id')}",
                location=listing.get('location'),
                seller=listing.get('seller', {}).get('username'),
                category=listing.get('category', 'Unknown'),
                description=listing.get('description', '').strip(),
                tags=listing.get('tags', []),
                raw_data=listing
            )
        except Exception as e:
            logger.error(f"Error processing listing: {str(e)}")
            return None

    async def search_sales(self, query: str, filters: Optional[SearchFilters] = None) -> List[Sale]:
        try:
            custom_url = await self.get_search_url(query)
            if not custom_url:
                return []

            raw_listings = await self.get_listings(custom_url)

            sales = []
            for raw_listing in raw_listings:
                sale = self.process_listing(raw_listing)
                if sale:
                    sales.append(sale)

            return sales

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None