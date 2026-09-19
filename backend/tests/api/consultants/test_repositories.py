from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from sqlalchemy import select

from app.consultants.models import Consultant
from app.consultants.repositories import (
    ConsultantFilters,
    ConsultantRepository,
)
from app.shared.schemas import (
    PaginationMetadata,
    PaginationParams,
    SortParams,
)


def make_db():
    db = MagicMock()
    db.execute = AsyncMock()
    return db


def make_result(first=None, scalar=None):
    result = MagicMock()

    scalars = MagicMock()
    scalars.first.return_value = first
    result.scalars.return_value = scalars

    result.scalar.return_value = scalar

    return result


def make_pagination_params():
    return PaginationParams(
        page=1,
        page_size=20,
    )


def make_sort_params():
    return SortParams(
        sort_by="created_at",
        sort_order="desc",
    )


class TestConsultantFilters:

    def test_apply_without_optional_filters(self):
        query = select(Consultant)

        filters = ConsultantFilters()

        result = filters.apply(query, Consultant)

        sql = str(result)

        assert "deleted_at IS NULL" in sql

    def test_apply_with_visa_status(self):
        query = select(Consultant)

        filters = ConsultantFilters(
            visa_status="H1B"
        )

        result = filters.apply(query, Consultant)

        sql = str(result)

        assert "deleted_at IS NULL" in sql
        assert "visa_status" in sql

    def test_apply_with_search(self):
        query = select(Consultant)

        filters = ConsultantFilters(
            search="john"
        )

        result = filters.apply(query, Consultant)

        sql = str(result)

        assert "deleted_at IS NULL" in sql
        assert "first_name" in sql
        assert "last_name" in sql
        assert "email" in sql

    def test_apply_with_all_filters(self):
        query = select(Consultant)

        filters = ConsultantFilters(
            visa_status="H1B",
            search="john",
        )

        result = filters.apply(query, Consultant)

        sql = str(result)

        assert "deleted_at IS NULL" in sql
        assert "visa_status" in sql
        assert "first_name" in sql
        assert "last_name" in sql
        assert "email" in sql


class TestConsultantRepository:

    def test_create_adds_consultant(self):
        db = make_db()

        repository = ConsultantRepository(db)

        consultant = repository.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        assert isinstance(consultant, Consultant)
        assert consultant.first_name == "John"
        assert consultant.last_name == "Doe"
        assert consultant.email == "john@example.com"

        db.add.assert_called_once_with(consultant)

    def test_model_cls(self):
        db = make_db()

        repository = ConsultantRepository(db)

        assert repository.model_cls is Consultant

    @pytest.mark.asyncio
    async def test_get_by_public_id_with_eager_load(self):
        db = make_db()

        consultant = SimpleNamespace(
            id=1,
            public_id=UUID(
                "11111111-1111-1111-1111-111111111111"
            ),
        )

        db.execute.return_value = make_result(
            first=consultant
        )

        repository = ConsultantRepository(db)

        result = await repository.get_by_public_id(
            consultant.public_id,
            eager_load_recruiter=True,
        )

        assert result == consultant
        db.execute.assert_awaited_once()

        query = db.execute.call_args.args[0]
        sql = str(query)

        assert "public_id" in sql
        assert "deleted_at IS NULL" in sql

    @pytest.mark.asyncio
    async def test_get_by_public_id_without_eager_load(self):
        db = make_db()

        consultant = SimpleNamespace(
            id=1,
            public_id=UUID(
                "11111111-1111-1111-1111-111111111111"
            ),
        )

        db.execute.return_value = make_result(
            first=consultant
        )

        repository = ConsultantRepository(db)

        result = await repository.get_by_public_id(
            consultant.public_id,
            eager_load_recruiter=False,
        )

        assert result == consultant
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_public_id_not_found(self):
        db = make_db()

        db.execute.return_value = make_result(
            first=None
        )

        repository = ConsultantRepository(db)

        result = await repository.get_by_public_id(
            UUID("11111111-1111-1111-1111-111111111111")
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_normalizes_email(self):
        db = make_db()

        consultant = SimpleNamespace(
            id=1,
            email="john@example.com",
        )

        db.execute.return_value = make_result(
            first=consultant
        )

        repository = ConsultantRepository(db)

        result = await repository.get_by_email(
            "  JOHN@EXAMPLE.COM  "
        )

        assert result == consultant
        db.execute.assert_awaited_once()

        query = db.execute.call_args.args[0]
        sql = str(query)

        assert "email" in sql
        assert "deleted_at IS NULL" in sql

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self):
        db = make_db()

        db.execute.return_value = make_result(
            first=None
        )

        repository = ConsultantRepository(db)

        result = await repository.get_by_email(
            "missing@example.com"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_exists_by_email_true(self):
        db = make_db()

        db.execute.return_value = make_result(
            scalar=True
        )

        repository = ConsultantRepository(db)

        result = await repository.exists_by_email(
            "  JOHN@EXAMPLE.COM  "
        )

        assert result is True
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exists_by_email_false(self):
        db = make_db()

        db.execute.return_value = make_result(
            scalar=False
        )

        repository = ConsultantRepository(db)

        result = await repository.exists_by_email(
            "missing@example.com"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_list_paginated_without_filters(self):
        db = make_db()

        repository = ConsultantRepository(db)

        pagination = make_pagination_params()
        sorting = make_sort_params()

        metadata = PaginationMetadata(
            page=1,
            page_size=20,
            total_items=0,
            total_pages=0,
            has_next=False,
            has_previous=False,
        )

        expected = ([], metadata)

        with patch(
            "app.consultants.repositories.paginate_repository_query",
            new=AsyncMock(return_value=expected),
        ) as paginate:

            result = await repository.list_paginated(
                pagination_params=pagination,
                sort_params=sorting,
                filter_params=None,
            )

        assert result == expected
        paginate.assert_awaited_once()

        kwargs = paginate.call_args.kwargs

        assert kwargs["db"] is db
        assert kwargs["model"] is Consultant
        assert kwargs["pagination_params"] is pagination
        assert kwargs["sort_params"] is sorting
        assert kwargs["filter_params"] is None

    @pytest.mark.asyncio
    async def test_list_paginated_with_filters(self):
        db = make_db()

        repository = ConsultantRepository(db)

        pagination = make_pagination_params()
        sorting = make_sort_params()

        filters = ConsultantFilters(
            visa_status="H1B",
            search="john",
        )

        metadata = PaginationMetadata(
            page=1,
            page_size=20,
            total_items=1,
            total_pages=1,
            has_next=False,
            has_previous=False,
        )

        expected = ([], metadata)

        with patch(
            "app.consultants.repositories.paginate_repository_query",
            new=AsyncMock(return_value=expected),
        ) as paginate:

            result = await repository.list_paginated(
                pagination_params=pagination,
                sort_params=sorting,
                filter_params=filters,
            )

        assert result == expected

        kwargs = paginate.call_args.kwargs

        assert kwargs["filter_params"] is filters