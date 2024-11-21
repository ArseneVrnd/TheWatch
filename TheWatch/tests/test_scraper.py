# tests/test_scraper.py
import pytest
from TheWatch.core.scraper import GrailedScraper
from TheWatch.core.models import SearchFilters

@pytest.mark.asyncio
async def test_scraper_initialization():
    scraper = GrailedScraper()
    assert scraper.base_url == "https://www.grailed.com"
    assert scraper.search_url == "https://www.grailed.com/shop"
    assert len(scraper.user_agents) > 0

@pytest.mark.asyncio
async def test_build_search_url():
    scraper = GrailedScraper()
    filters = SearchFilters(
        min_price=100,
        max_price=500,
        designers=['Nike']
    )
    url = scraper._build_search_url("test query", filters, page=1)
    assert "test query" in url
    assert "price[min]=100" in url
    assert "price[max]=500" in url
