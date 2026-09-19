from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.marketing.repository import MarketingActivityRepository


def make_repository():
    db = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    return db, MarketingActivityRepository(db)


@pytest.mark.asyncio
async def test_create():
    db, repository = make_repository()

    result = await repository.create(
        consultant_id=1,
        vendor_id=2,
        vendor_contact_id=3,
        client_id=4,
        performed_by=5,
        activity_type="CALL",
        channel="PHONE",
        outcome="CONNECTED",
        subject="Follow-up",
        notes="Discussed requirement",
        follow_up_required=True,
        occurred_at="2026-01-01",
    )

    db.add.assert_called_once()
    db.flush.assert_awaited_once()

    assert result.consultant_id == 1
    assert result.vendor_id == 2
    assert result.vendor_contact_id == 3
    assert result.client_id == 4
    assert result.performed_by == 5
    assert result.activity_type == "CALL"
    assert result.channel == "PHONE"
    assert result.outcome == "CONNECTED"
    assert result.subject == "Follow-up"
    assert result.notes == "Discussed requirement"
    assert result.follow_up_required is True
    assert result.occurred_at == "2026-01-01"


@pytest.mark.asyncio
async def test_create_allows_optional_relationships():
    db, repository = make_repository()

    result = await repository.create(
        consultant_id=10,
        vendor_id=20,
        vendor_contact_id=None,
        client_id=None,
        performed_by=30,
        activity_type="EMAIL",
        channel="EMAIL",
        outcome="SENT",
        subject=None,
        notes=None,
        follow_up_required=False,
        occurred_at=None,
    )

    assert result.vendor_contact_id is None
    assert result.client_id is None
    assert result.subject is None
    assert result.notes is None
    assert result.follow_up_required is False
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_public_id():
    db, repository = make_repository()

    activity = SimpleNamespace(public_id=uuid4())

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.first.return_value = activity
    db.execute.return_value = result_proxy

    result = await repository.get_by_public_id(activity.public_id)

    assert result is activity
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_public_id_not_found():
    db, repository = make_repository()

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.first.return_value = None
    db.execute.return_value = result_proxy

    result = await repository.get_by_public_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_list_by_consultant():
    db, repository = make_repository()

    activities = [
        SimpleNamespace(id=1),
        SimpleNamespace(id=2),
    ]

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = activities
    db.execute.return_value = result_proxy

    result = await repository.list_by_consultant(10)

    assert result == activities
    assert len(result) == 2
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_by_consultant_empty():
    db, repository = make_repository()

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = []
    db.execute.return_value = result_proxy

    result = await repository.list_by_consultant(999)

    assert result == []