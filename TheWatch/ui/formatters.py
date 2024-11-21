# TheWatch/ui/formatters.py
from typing import Union, Optional
from datetime import datetime
import re

def format_price(price: Union[float, int], currency: str = "$") -> str:
    """Format price with currency symbol"""
    return f"{currency}{price:,.2f}"

def format_date(date: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format date for display"""
    return date.strftime(format_str)

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format percentage value"""
    return f"{value:.{decimal_places}f}%"

def format_condition(condition: str) -> str:
    """Format condition string for display"""
    # Convert snake_case or kebab-case to Title Case
    condition = re.sub(r'[_-]', ' ', condition)
    return condition.title()

def format_title(title: str, max_length: int = 50) -> str:
    """Format title with optional truncation"""
    if len(title) > max_length:
        return f"{title[:max_length-3]}..."
    return title

def format_location(location: Optional[str], default: str = "Unknown") -> str:
    """Format location with default value"""
    if not location:
        return default
    return location.strip()

def format_size(size: Union[str, int, float]) -> str:
    """Format size for display"""
    if isinstance(size, (int, float)):
        return str(size)
    return size.upper()

def format_discount(original: float, current: float) -> str:
    """Format discount percentage"""
    if original <= current:
        return "0% off"
    discount = ((original - current) / original) * 100
    return f"{discount:.1f}% off"