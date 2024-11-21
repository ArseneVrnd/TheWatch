from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class SearchFilters:
    """Search filters for Grailed"""
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    designers: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    sizes: Optional[List[str]] = None

@dataclass
class Sale:
    """Represents a single sale from Grailed"""
    id: int
    title: str
    price: float
    original_price: float
    designer: str
    size: str
    condition: str
    location: str
    seller: str
    url: str
    photos: List[str]
    created_at: datetime
    category: str
    description: str
    discount: Optional[float] = None
    discount_percentage: Optional[float] = None