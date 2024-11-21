# TheWatch/data/processors.py
from typing import Dict, Any, Optional
from datetime import datetime

from TheWatch.core.models import Sale
from TheWatch.utils.logger import setup_logger
from TheWatch.utils.helpers import clean_text, parse_price

logger = setup_logger(__name__)


def process_raw_listing(raw_data: Dict[str, Any]) -> Optional[Sale]:
    """Process raw listing data into a Sale object"""
    try:
        price = parse_price(raw_data.get('price', '0'))
        original_price = parse_price(raw_data.get('original_price', str(price)))

        sale_data = {
            'title': clean_text(raw_data.get('title', '')),
            'price': price,
            'original_price': original_price,
            'sold_date': datetime.fromisoformat(raw_data.get('sold_date', datetime.now().isoformat())),
            'designer': raw_data.get('designer_names', ['Unknown'])[0],
            'size': str(raw_data.get('size', 'Unknown')),
            'condition': raw_data.get('condition', 'Unknown'),
            'url': f"https://www.grailed.com/listings/{raw_data.get('id')}",
            'location': raw_data.get('location'),
            'seller': raw_data.get('seller', {}).get('username'),
            'category': raw_data.get('category_path', ['Unknown'])[0],
            'description': clean_text(raw_data.get('description', '')),
            'tags': raw_data.get('tags', []),
            'raw_data': raw_data
        }

        return Sale(**sale_data)
    except Exception as e:
        logger.error(f"Error processing raw listing: {str(e)}")
        return None