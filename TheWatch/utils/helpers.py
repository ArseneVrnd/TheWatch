# TheWatch/utils/helpers.py
import re
from typing import Optional, Union
from datetime import datetime

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def parse_price(price_str: str) -> Optional[float]:
    """Parse price string to float"""
    if not price_str:
        return None
    try:
        # Remove currency symbols and commas
        clean_price = re.sub(r'[^\d.]', '', price_str)
        return float(clean_price)
    except (ValueError, TypeError):
        return None

def format_date(date: Union[str, datetime]) -> str:
    """Format date consistently"""
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except ValueError:
            return date
    return date.strftime('%Y-%m-%d %H:%M:%S')

def parse_condition(condition: str) -> str:
    """Parse and standardize condition string"""
    condition = condition.lower()
    if 'new' in condition:
        return 'is_new'
    elif 'gently' in condition:
        return 'is_gently_used'
    elif 'used' in condition:
        return 'is_used'
    elif 'worn' in condition:
        return 'is_very_worn'
    return condition

def parse_size(size: str) -> str:
    """Parse and standardize size string"""
    size = str(size).upper().strip()
    # Remove common prefixes
    size = re.sub(r'^(US|EU|UK|JP)\s*', '', size)
    return size

# Export functions
__all__ = [
    'clean_text',
    'parse_price',
    'format_date',
    'parse_condition',
    'parse_size'
]