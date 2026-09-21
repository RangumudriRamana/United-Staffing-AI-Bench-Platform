from unittest.mock import AsyncMock, MagicMock

import pytest

from app.communications.router import (
    create_shared_internal_note,
    get_unified_entity_interaction_timeline,
)


@pytest.mark.asyncio
async def test_create_shared_internal_note():
    service = MagicMock()
    service.record_internal_note = AsyncMock(return_value={"id": 1})

    payload = MagicMock()
    current_user = MagicMock()
    current_user.id = 10

    result = await create_shared_internal_note(
        payload=payload,
        current_user=current_user,
        service=service,
        _role=MagicMock(),
    )

    assert result == {"id": 1}
    service.record_internal_note.assert_awaited_once_with(
        payload=payload,
        author_user_id=10,
    )


@pytest.mark.asyncio
async def test_get_unified_entity_interaction_timeline():
    service = MagicMock()
    service.fetch_entity_unified_timeline = AsyncMock(
        return_value=[{"id": 1}]
    )

    result = await get_unified_entity_interaction_timeline(
        entity_type="consultant",
        entity_id=5,
        service=service,
        _role=MagicMock(),
    )

    assert result == [{"id": 1}]
    service.fetch_entity_unified_timeline.assert_awaited_once_with(
        entity_type="consultant",
        entity_id=5,
    )