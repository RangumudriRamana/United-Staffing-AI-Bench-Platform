from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.submissions.repositories import SubmissionRepository


def make_repository():
    db = MagicMock()
    db.execute = AsyncMock()
    return SubmissionRepository(db), db


@pytest.mark.asyncio
async def test_get_by_public_id_without_eager_loading():
    repository, db = make_repository()

    result = MagicMock()
    submission = MagicMock()

    result.scalars.return_value.first.return_value = submission
    db.execute.return_value = result

    public_id = __import__("uuid").uuid4()

    returned = await repository.get_by_public_id(public_id)

    assert returned is submission
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_public_id_with_eager_loading():
    repository, db = make_repository()

    result = MagicMock()
    submission = MagicMock()

    result.scalars.return_value.first.return_value = submission
    db.execute.return_value = result

    public_id = __import__("uuid").uuid4()

    returned = await repository.get_by_public_id(
        public_id,
        eager_load_details=True,
    )

    assert returned is submission
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_exists_active_submission_returns_true():
    repository, db = make_repository()

    result = MagicMock()
    result.scalar.return_value = True
    db.execute.return_value = result

    returned = await repository.exists_active_submission(
        consultant_id=1,
        client_id=2,
        job_title="Senior Java Developer",
    )

    assert returned is True
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_exists_active_submission_returns_false_when_scalar_is_false():
    repository, db = make_repository()

    result = MagicMock()
    result.scalar.return_value = False
    db.execute.return_value = result

    returned = await repository.exists_active_submission(
        consultant_id=1,
        client_id=2,
        job_title="Senior Java Developer",
    )

    assert returned is False
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_submissions_paginated_delegates_to_shared_pagination():
    repository, db = make_repository()

    criteria = MagicMock()
    pagination = MagicMock()
    sort = MagicMock()

    expected_records = [MagicMock()]
    expected_metadata = SimpleNamespace(total_items=1)

    from unittest.mock import patch

    with patch(
        "app.submissions.repositories.paginate_repository_query",
        new_callable=AsyncMock,
        return_value=(expected_records, expected_metadata),
    ) as paginate_mock:
        returned = await repository.list_submissions_paginated(
            criteria,
            pagination,
            sort,
        )

    assert returned == (expected_records, expected_metadata)
    paginate_mock.assert_awaited_once()

    call_kwargs = paginate_mock.call_args.kwargs
    assert call_kwargs["db"] is db
    assert call_kwargs["model"].__name__ == "Submission"
    assert call_kwargs["pagination_params"] is pagination
    assert call_kwargs["sort_params"] is sort
    assert call_kwargs["filter_params"] is None