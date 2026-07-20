from typing import Any, Protocol, TypeVar
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.schemas import PaginationParams, SortParams, PaginationMetadata
from app.shared.pagination import calculate_metadata
from app.shared.sorting import apply_sorting_to_query

class FilterableRequest(Protocol):
    """Structural type contract enabling any arbitrary filtering object to pass smoothly."""
    def apply(self, query: Select, model: Any) -> Select: ...


async def paginate_repository_query(
    db: AsyncSession,
    query: Select,
    model: Any,
    pagination_params: PaginationParams,
    sort_params: SortParams,
    filter_params: FilterableRequest | None = None
) -> tuple[list[Any], PaginationMetadata]:
    """
    Orchestrates the complete compilation lifecycle of an incoming query.
    Extracts counts, injects filters, orders fields, and chunks execution windows.
    """
    # 1. Inject application filter constraints if present
    if filter_params and hasattr(filter_params, "apply"):
        query = filter_params.apply(query, model)

    # 2. Programmatically compile the count query baseline
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_items = count_result.scalar_one()

    # 3. Inject structural sorting indicators
    query = apply_sorting_to_query(query, model, sort_params.sort_by, sort_params.sort_order)

    # 4. Inject standard execution offsets
    offset_value = (pagination_params.page - 1) * pagination_params.page_size
    query = query.offset(offset_value).limit(pagination_params.page_size)

    # 5. Execute payload extraction
    payload_result = await db.execute(query)
    extracted_rows = list(payload_result.scalars().all())

    # 6. Build the metadata envelope contract
    metadata = calculate_metadata(total_items, pagination_params.page, pagination_params.page_size)

    return extracted_rows, metadata