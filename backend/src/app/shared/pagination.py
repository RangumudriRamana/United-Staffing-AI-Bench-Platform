import math
from app.shared.schemas import PaginationMetadata

def calculate_metadata(total_items: int, page: int, page_size: int) -> PaginationMetadata:
    """Calculates frontend-friendly pagination indicators based on total row counts."""
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    
    return PaginationMetadata(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )