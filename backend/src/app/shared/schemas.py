from typing import Generic, TypeVar, Literal
from pydantic import BaseModel, Field
from app.shared.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

class SortParams(BaseModel):
    sort_by: str | None = None
    sort_order: Literal["asc", "desc"] = "asc"

class SearchParams(BaseModel):
    search: str | None = None

class PaginationMetadata(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class PagedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMetadata