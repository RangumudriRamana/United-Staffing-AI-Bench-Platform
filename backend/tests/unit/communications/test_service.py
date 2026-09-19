from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.communications.enums import CommunicationDirection, CommunicationType
from app.communications.models import Communication
from app.communications.schemas import InternalNoteRequest
from app.communications.service import CommunicationService


def make_service():
    db = MagicMock()
    db.commit = AsyncMock()
    db.execute = AsyncMock()
    service = CommunicationService(db)
    return service, db


@pytest.mark.asyncio
async def test_record_internal_note_creates_and_commits_note():
    service, db = make_service()

    payload = InternalNoteRequest(
        related_entity_type=" consultant ",
        related_entity_id=123,
        subject="Follow-up Required",
        body_preview="Contact consultant regarding availability.",
    )

    result = await service.record_internal_note(
        payload=payload,
        author_user_id=456,
    )

    assert isinstance(result, Communication)
    assert result.sender_user_id == 456
    assert result.communication_type == CommunicationType.INTERNAL_NOTE
    assert result.direction == CommunicationDirection.INTERNAL
    assert result.subject == "Follow-up Required"
    assert result.body_preview == "Contact consultant regarding availability."
    assert result.related_entity_type == "CONSULTANT"
    assert result.related_entity_id == 123
    assert result.occurred_at is not None
    assert result.occurred_at.tzinfo is not None

    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_record_internal_note_normalizes_entity_type():
    service, db = make_service()

    payload = InternalNoteRequest(
        related_entity_type="  vendor  ",
        related_entity_id=55,
        subject="Vendor Note",
        body_preview="Internal vendor communication.",
    )

    result = await service.record_internal_note(
        payload=payload,
        author_user_id=10,
    )

    assert result.related_entity_type == "VENDOR"
    assert result.related_entity_id == 55


@pytest.mark.asyncio
async def test_fetch_entity_unified_timeline_delegates_to_composer(
    monkeypatch,
):
    service, db = make_service()

    records = [MagicMock(), MagicMock()]
    expected_timeline = [
        {
            "source": "COMMUNICATION",
            "public_id": "abc",
            "type": "INTERNAL_NOTE",
        }
    ]

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = records
    db.execute = AsyncMock(return_value=result_mock)

    composer_mock = MagicMock(
        return_value=expected_timeline
    )

    monkeypatch.setattr(
        "app.communications.service.TimelineComposer.merge_and_sort_activities",
        composer_mock,
    )

    result = await service.fetch_entity_unified_timeline(
        entity_type=" consultant ",
        entity_id=123,
    )

    assert result == expected_timeline

    composer_mock.assert_called_once_with(records)
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_entity_unified_timeline_returns_empty_list():
    service, db = make_service()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.fetch_entity_unified_timeline(
        entity_type="vendor",
        entity_id=55,
    )

    assert result == []