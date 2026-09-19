from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.consultants.router import (
    archive_consultant,
    create_consultant,
    get_consultant,
    get_consultant_marketing_history,
    list_consultants,
    transition_consultant_status,
    update_consultant,
)


@pytest.mark.asyncio
async def test_get_consultant_marketing_history():
    service = MagicMock()
    service.get_marketing_history = AsyncMock(
        return_value=["history-1", "history-2"]
    )

    public_id = uuid4()

    result = await get_consultant_marketing_history(
        public_id=public_id,
        service=service,
    )

    assert result == ["history-1", "history-2"]
    service.get_marketing_history.assert_awaited_once_with(public_id)


@pytest.mark.asyncio
async def test_create_consultant():
    service = MagicMock()
    service.create_consultant = AsyncMock(
        return_value="consultant"
    )

    payload = MagicMock()
    current_user = MagicMock()
    current_user.id = 101

    result = await create_consultant(
        payload=payload,
        service=service,
        current_user=current_user,
    )

    assert result == "consultant"

    service.create_consultant.assert_awaited_once_with(
        payload,
        current_user_id=101,
    )


@pytest.mark.asyncio
async def test_get_consultant():
    service = MagicMock()
    service.get_consultant = AsyncMock(
        return_value="consultant"
    )

    public_id = uuid4()

    result = await get_consultant(
        public_id=public_id,
        service=service,
    )

    assert result == "consultant"
    service.get_consultant.assert_awaited_once_with(public_id)


@pytest.mark.asyncio
async def test_list_consultants():
    service = MagicMock()
    service.list_consultants = AsyncMock(
        return_value=(
            ["consultant-1", "consultant-2"],
            "metadata",
        )
    )

    pagination = MagicMock()
    sort = MagicMock()
    filters = MagicMock()

    result = await list_consultants(
        pagination=pagination,
        sort=sort,
        filters=filters,
        service=service,
    )

    assert result == {
        "data": ["consultant-1", "consultant-2"],
        "pagination": "metadata",
    }

    service.list_consultants.assert_awaited_once_with(
        pagination,
        sort,
        filters,
    )


@pytest.mark.asyncio
async def test_update_consultant():
    service = MagicMock()
    service.update_consultant = AsyncMock(
        return_value="updated-consultant"
    )

    public_id = uuid4()
    payload = MagicMock()

    current_user = MagicMock()
    current_user.id = 202

    result = await update_consultant(
        public_id=public_id,
        payload=payload,
        service=service,
        current_user=current_user,
    )

    assert result == "updated-consultant"

    service.update_consultant.assert_awaited_once_with(
        public_id,
        payload,
        current_user_id=202,
    )


@pytest.mark.asyncio
async def test_archive_consultant():
    service = MagicMock()
    service.archive_consultant = AsyncMock()

    public_id = uuid4()

    current_user = MagicMock()
    current_user.id = 303

    result = await archive_consultant(
        public_id=public_id,
        service=service,
        current_user=current_user,
    )

    assert result is None

    service.archive_consultant.assert_awaited_once_with(
        public_id,
        current_user_id=303,
    )


@pytest.mark.asyncio
async def test_transition_consultant_status():
    service = MagicMock()
    service.transition_marketing_status = AsyncMock(
        return_value="transitioned-consultant"
    )

    public_id = uuid4()

    payload = MagicMock()
    payload.target_status = "MARKETED"
    payload.reason = "New opportunity"
    payload.notes = "Ready for submission"

    current_user = MagicMock()
    current_user.id = 404

    result = await transition_consultant_status(
        public_id=public_id,
        payload=payload,
        service=service,
        current_user=current_user,
    )

    assert result == "transitioned-consultant"

    service.transition_marketing_status.assert_awaited_once_with(
        public_id=public_id,
        new_status=payload.target_status,
        changed_by_user_id=404,
        reason=payload.reason,
        notes=payload.notes,
    )


@pytest.mark.asyncio
async def test_get_consultant_marketing_history_returns_empty_list():
    service = MagicMock()
    service.get_marketing_history = AsyncMock(return_value=[])

    public_id = uuid4()

    result = await get_consultant_marketing_history(
        public_id=public_id,
        service=service,
    )

    assert result == []
    service.get_marketing_history.assert_awaited_once_with(public_id)