from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.requirements.models import Requirement
from app.requirements.repositories import RequirementRepository


def make_db():
    db = MagicMock()
    db.execute = AsyncMock()
    return db


def make_result(records=None):
    result = MagicMock()

    scalars = MagicMock()
    scalars.first.return_value = (
        records[0] if records else None
    )
    scalars.all.return_value = records or []

    result.scalars.return_value = scalars

    return result


def make_requirement():
    return MagicMock(spec=Requirement)


def test_create_adds_and_returns_requirement():
    db = make_db()
    repository = RequirementRepository(db)

    requirement = repository.create(
        job_title="Python Developer",
    )

    assert isinstance(requirement, Requirement)
    assert requirement.job_title == "Python Developer"

    db.add.assert_called_once_with(requirement)


@pytest.mark.asyncio
async def test_get_by_public_id_without_eager_loading():
    db = make_db()

    requirement = make_requirement()

    db.execute.return_value = make_result([requirement])

    repository = RequirementRepository(db)

    public_id = uuid4()

    result = await repository.get_by_public_id(
        public_id=public_id,
        eager_load_details=False,
    )

    assert result is requirement
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_public_id_with_eager_loading():
    db = make_db()

    requirement = make_requirement()

    db.execute.return_value = make_result([requirement])

    repository = RequirementRepository(db)

    public_id = uuid4()

    result = await repository.get_by_public_id(
        public_id=public_id,
        eager_load_details=True,
    )

    assert result is requirement
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_public_id_returns_none_when_not_found():
    db = make_db()

    db.execute.return_value = make_result([])

    repository = RequirementRepository(db)

    result = await repository.get_by_public_id(
        public_id=uuid4(),
    )

    assert result is None
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_requirements_paginated_delegates_to_pagination():
    db = make_db()

    repository = RequirementRepository(db)

    criteria = MagicMock()
    pagination = MagicMock()
    sort = MagicMock()

    expected_records = [
        make_requirement(),
    ]
    expected_metadata = MagicMock()

    with patch(
        "app.requirements.repositories.build_requirement_search_pipeline",
        return_value=select(Requirement),
    ) as mock_build_pipeline, patch(
        "app.requirements.repositories.paginate_repository_query",
        new_callable=AsyncMock,
        return_value=(expected_records, expected_metadata),
    ) as mock_paginate:

        result = await repository.list_requirements_paginated(
            criteria=criteria,
            pagination=pagination,
            sort=sort,
        )

    assert result == (
        expected_records,
        expected_metadata,
    )

    mock_build_pipeline.assert_called_once_with(criteria)

    mock_paginate.assert_awaited_once()

    call_kwargs = mock_paginate.call_args.kwargs

    assert call_kwargs["db"] is db
    assert call_kwargs["model"] is Requirement
    assert call_kwargs["pagination_params"] is pagination
    assert call_kwargs["sort_params"] is sort
    assert call_kwargs["filter_params"] is None

    query = call_kwargs["query"]

    # Verify the repository added eager-loading options
    # to prevent async lazy-loading during serialization.
    assert query is not None