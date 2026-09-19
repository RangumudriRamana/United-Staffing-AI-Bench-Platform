from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.marketing.router import (
    create_marketing_activity,
    list_consultant_marketing_activities,
    get_marketing_activity,
)


@pytest.mark.asyncio
async def test_create_marketing_activity():
    payload = SimpleNamespace()
    current_user = SimpleNamespace(id=101)
    expected = {"public_id": "activity-1"}

    service = SimpleNamespace(
        create_activity=AsyncMock(return_value=expected)
    )

    result = await create_marketing_activity(
        payload=payload,
        current_user=current_user,
        service=service,
        _role=None,
    )

    assert result == expected
    service.create_activity.assert_awaited_once_with(
        payload=payload,
        current_user_id=101,
    )


@pytest.mark.asyncio
async def test_list_consultant_marketing_activities():
    consultant_public_id = uuid4()
    expected = [{"public_id": "activity-1"}]

    service = SimpleNamespace(
        list_consultant_activities=AsyncMock(return_value=expected)
    )

    result = await list_consultant_marketing_activities(
        consultant_public_id=consultant_public_id,
        current_user=SimpleNamespace(id=101),
        service=service,
        _role=None,
    )

    assert result == expected
    service.list_consultant_activities.assert_awaited_once_with(
        consultant_public_id=consultant_public_id,
    )


@pytest.mark.asyncio
async def test_get_marketing_activity():
    public_id = uuid4()
    expected = {"public_id": str(public_id)}

    service = SimpleNamespace(
        get_activity=AsyncMock(return_value=expected)
    )

    result = await get_marketing_activity(
        public_id=public_id,
        current_user=SimpleNamespace(id=101),
        service=service,
        _role=None,
    )

    assert result == expected
    service.get_activity.assert_awaited_once_with(
        public_id=public_id,
    )


@pytest.mark.asyncio
async def test_get_marketing_activity_propagates_error():
    public_id = uuid4()

    service = SimpleNamespace(
        get_activity=AsyncMock(
            side_effect=ValueError("activity failure")
        )
    )

    with pytest.raises(ValueError, match="activity failure"):
        await get_marketing_activity(
            public_id=public_id,
            current_user=SimpleNamespace(id=101),
            service=service,
            _role=None,
        )