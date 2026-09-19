from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import declarative_base

from app.shared.query_builder import paginate_repository_query
from app.shared.schemas import PaginationParams, SortParams


Base = declarative_base()


class TestModel(Base):
    __tablename__ = "test_query_builder_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class ModelWithoutId:
    name = Column(String)


def make_db():
    db = MagicMock()
    db.execute = AsyncMock()
    return db


def make_result(*, scalar_value=None, rows=None):
    result = MagicMock()

    if scalar_value is not None:
        result.scalar_one.return_value = scalar_value

    result.scalars.return_value.all.return_value = rows or []

    return result


@pytest.mark.asyncio
async def test_paginate_repository_query_without_filters():
    db = make_db()

    rows = ["row1", "row2"]

    db.execute.side_effect = [
        make_result(scalar_value=25),
        make_result(rows=rows),
    ]

    pagination = PaginationParams(
        page=2,
        page_size=10,
    )

    sorting = SortParams(
        sort_by="name",
        sort_order="asc",
    )

    query = select(TestModel)

    extracted, metadata = await paginate_repository_query(
        db=db,
        query=query,
        model=TestModel,
        pagination_params=pagination,
        sort_params=sorting,
    )

    assert extracted == rows
    assert metadata.total_items == 25
    assert metadata.page == 2
    assert metadata.page_size == 10

    assert db.execute.await_count == 2


@pytest.mark.asyncio
async def test_paginate_repository_query_applies_filter():
    db = make_db()

    rows = ["filtered"]

    db.execute.side_effect = [
        make_result(scalar_value=1),
        make_result(rows=rows),
    ]

    filter_params = MagicMock()
    filter_params.apply.return_value = select(TestModel).where(
        TestModel.name == "filtered"
    )

    pagination = PaginationParams(
        page=1,
        page_size=10,
    )

    sorting = SortParams(
        sort_by="name",
        sort_order="asc",
    )

    query = select(TestModel)

    extracted, metadata = await paginate_repository_query(
        db=db,
        query=query,
        model=TestModel,
        pagination_params=pagination,
        sort_params=sorting,
        filter_params=filter_params,
    )

    assert extracted == rows
    assert metadata.total_items == 1

    filter_params.apply.assert_called_once()

    assert db.execute.await_count == 2


@pytest.mark.asyncio
async def test_paginate_repository_query_ignores_object_without_apply():
    db = make_db()

    db.execute.side_effect = [
        make_result(scalar_value=0),
        make_result(rows=[]),
    ]

    pagination = PaginationParams(
        page=1,
        page_size=20,
    )

    sorting = SortParams(
        sort_by=None,
        sort_order="desc",
    )

    query = select(TestModel)

    filter_params = object()

    extracted, metadata = await paginate_repository_query(
        db=db,
        query=query,
        model=TestModel,
        pagination_params=pagination,
        sort_params=sorting,
        filter_params=filter_params,
    )

    assert extracted == []
    assert metadata.total_items == 0
    assert metadata.page == 1
    assert metadata.page_size == 20

    assert db.execute.await_count == 2


@pytest.mark.asyncio
async def test_paginate_repository_query_applies_offset_and_limit():
    db = make_db()

    db.execute.side_effect = [
        make_result(scalar_value=100),
        make_result(rows=["page"]),
    ]

    pagination = PaginationParams(
        page=3,
        page_size=20,
    )

    sorting = SortParams(
        sort_by="id",
        sort_order="desc",
    )

    query = select(TestModel)

    extracted, metadata = await paginate_repository_query(
        db=db,
        query=query,
        model=TestModel,
        pagination_params=pagination,
        sort_params=sorting,
    )

    assert extracted == ["page"]
    assert metadata.total_items == 100
    assert metadata.page == 3
    assert metadata.page_size == 20

    executed_payload_query = db.execute.await_args_list[1].args[0]
    compiled_sql = str(executed_payload_query)

    assert "LIMIT" in compiled_sql
    assert "OFFSET" in compiled_sql