from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.communications.router import (
    create_shared_internal_note,
    get_unified_entity_interaction_timeline,
)


@pytest.mark.asyncio
async def test_create_shared_internal_note():
    payload = SimpleNamespace(
        subject="Test note",
        body_preview="Internal communication",
        related_entity_type="consultant",
        related_entity_id=10,
    )
    expected = {"public_id": "note-1"}

    service = SimpleNamespace(
        record_internal_note=AsyncMock(return_value=expected)
    )
    current_user = SimpleNamespace(id=25)

    result = await create_shared_internal_note(
        payload=payload,
        current_user=current_user,
        service=service,
        _role=None,
    )

    assert result == expected
    service.record_internal_note.assert_awaited_once_with(
        payload=payload,
        author_user_id=25,
    )


@pytest.mark.asyncio
async def test_get_unified_entity_interaction_timeline():
    expected = [
        {"source": "COMMUNICATION", "title": "Test", "timestamp": "2026-01-01T00:00:00+00:00"}
    ]

    service = SimpleNamespace(
        fetch_entity_unified_timeline=AsyncMock(return_value=expected)
    )

    result = await get_unified_entity_interaction_timeline(
        entity_type="consultant",
        entity_id=10,
        service=service,
        _role=None,
    )

    assert result == expected
    service.fetch_entity_unified_timeline.assert_awaited_once_with(
        entity_type="consultant",
        entity_id=10,
    )


@pytest.mark.asyncio
async def test_get_unified_entity_interaction_timeline_passes_entity_values_unchanged():
    service = SimpleNamespace(
        fetch_entity_unified_timeline=AsyncMock(return_value=[])
    )

    await get_unified_entity_interaction_timeline(
        entity_type=" vendor ",
        entity_id=999,
        service=service,
        _role=None,
    )

    service.fetch_entity_unified_timeline.assert_awaited_once_with(
        entity_type=" vendor ",
        entity_id=999,
    )


@pytest.mark.asyncio
async def test_create_shared_internal_note_propagates_service_error():
    payload = SimpleNamespace(
        subject="Test",
        body_preview="Body",
        related_entity_type="vendor",
        related_entity_id=5,
    )

    service = SimpleNamespace(
        record_internal_note=AsyncMock(
            side_effect=HTTPException(status_code=400, detail="Invalid note")
        )
    )
    current_user = SimpleNamespace(id=7)

    with pytest.raises(HTTPException) as exc_info:
        await create_shared_internal_note(
            payload=payload,
            current_user=current_user,
            service=service,
            _role=None,
        )

    assert exc_info.value.status_code == 400