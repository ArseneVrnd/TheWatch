from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging
from thewatch.core.api import GrailedAPI
from thewatch.core.models import SearchFilters, Sale
from pydantic import BaseModel
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class SalesResponse(BaseModel):
    success: bool
    sales: List[dict]
    message: Optional[str] = None


@router.get("/search", response_model=SalesResponse)
async def search(
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        condition: Optional[str] = None
):
    api = GrailedAPI()
    try:
        filters = SearchFilters(
            min_price=min_price,
            max_price=max_price,
            conditions=[condition] if condition else None
        )

        sales = await api.search_sales(query, filters)
        if not sales:
            return SalesResponse(success=True, sales=[], message="No results found")

        return SalesResponse(
            success=True,
            sales=[sale.__dict__ for sale in sales]
        )

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing search: {str(e)}"
        )
    finally:
        await api.close()