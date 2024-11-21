# tests/test_exporters.py
import pytest
from pathlib import Path
from TheWatch.data.exporters import SalesExporter
from TheWatch.core.models import Sale
from datetime import datetime

@pytest.fixture
def sample_sales():
    return [
        Sale(
            title="Test Item 1",
            price=100.0,
            original_price=150.0,
            sold_date=datetime.now(),
            designer="Nike",
            size="L",
            condition="is_new",
            url="https://example.com/1"
        ),
        Sale(
            title="Test Item 2",
            price=200.0,
            original_price=250.0,
            sold_date=datetime.now(),
            designer="Adidas",
            size="M",
            condition="is_used",
            url="https://example.com/2"
        )
    ]

def test_csv_export(sample_sales, tmp_path):
    exporter = SalesExporter(output_dir=str(tmp_path))
    filepath = exporter.export_csv(sample_sales, "test")
    assert Path(filepath).exists()
    assert Path(filepath).suffix == ".csv"

@pytest.mark.skipif(
    ImportError,
    reason="pandas and openpyxl required for Excel export"
)
def test_excel_export(sample_sales, tmp_path):
    exporter = SalesExporter(output_dir=str(tmp_path))
    filepath = exporter.export_excel(sample_sales, "test")
    assert Path(filepath).exists()
    assert Path(filepath).suffix == ".xlsx"