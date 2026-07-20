from typing import Any
from sqlalchemy import Select

def apply_sorting_to_query(query: Select, model: Any, sort_by: str | None, sort_order: str) -> Select:
    """Safely binds column order attributes to a working SQLAlchemy query object."""
    if not sort_by or not hasattr(model, sort_by):
        # Fall back gracefully to primary key identifier ordering if target column is invalid
        if hasattr(model, "id"):
            return query.order_by(model.id.desc())
        return query

    column = getattr(model, sort_by)
    direction = column.desc() if sort_order == "desc" else column.asc()
    return query.order_by(direction)