# tests/test_models.py
import pytest
from datetime import datetime
from TheWatch.core.models import Sale, SearchFilters


def test_sale_properties():
    sale = Sale(
        title="Test Item",
        price=100.0,
        original_price=150.0,
        sold_date=datetime.now(),
        designer="N",
        size="L",
        condition="is_new",
        url="https://example.com"
    )

    assert sale.discount_amount == 50.0
    assert sale.discount_percentage == pytest.approx(33.33, rel=0.01)
    assert sale.designer_display == "New Balance"
    assert sale.condition_display == "New"