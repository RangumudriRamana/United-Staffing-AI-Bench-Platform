from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.consultants.enums import AvailabilityStatus, MarketingStatus
from app.consultants.service import ConsultantService
from app.core.exceptions import AppException


def make_consultant(
    *,
    public_id="11111111-1111-1111-1111-111111111111",
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    expected_rate=Decimal("75"),
    marketing_status=MarketingStatus.NEW,
    availability_status=AvailabilityStatus.AVAILABLE_NOW,
):
    consultant = MagicMock()
    consultant.id = 1
    consultant.public_id = public_id
    consultant.first_name = first_name
    consultant.last_name = last_name
    consultant.email = email
    consultant.phone = "9999999999"
    consultant.visa_status = MagicMock(value="H1B")
    consultant.marketing_status = marketing_status
    consultant.availability_status = availability_status
    consultant.expected_rate = expected_rate
    consultant.availability_date = None
    consultant.updated_by = None
    return consultant


@pytest.fixture
def service():
    db = AsyncMock()
    svc = ConsultantService(db)

    svc.repo = MagicMock()
    svc.audit_service = MagicMock()

    svc.repo.exists_by_email = AsyncMock(return_value=False)
    svc.repo.get_by_public_id = AsyncMock()
    svc.repo.list_paginated = AsyncMock()
    svc.audit_service.write_audit_entry = AsyncMock()
    svc.audit_service.get_next_entity_version = AsyncMock(return_value=1)

    return svc


# ---------------------------------------------------------------------------
# Audit snapshot
# ---------------------------------------------------------------------------


def test_consultant_audit_snapshot_with_expected_rate(service):
    consultant = make_consultant(expected_rate=Decimal("80.50"))

    snapshot = service._consultant_audit_snapshot(consultant)

    assert snapshot["public_id"] == str(consultant.public_id)
    assert snapshot["first_name"] == "John"
    assert snapshot["last_name"] == "Doe"
    assert snapshot["email"] == "john@example.com"
    assert snapshot["expected_rate"] == "80.50"
    assert snapshot["marketing_status"] == MarketingStatus.NEW.value
    assert snapshot["availability_status"] == AvailabilityStatus.AVAILABLE_NOW.value


def test_consultant_audit_snapshot_without_expected_rate(service):
    consultant = make_consultant(expected_rate=None)

    snapshot = service._consultant_audit_snapshot(consultant)

    assert snapshot["expected_rate"] is None


# ---------------------------------------------------------------------------
# Create consultant
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_consultant_success(service):
    payload = MagicMock()
    payload.email = "john@example.com"
    payload.expected_rate = Decimal("75")
    payload.model_dump.return_value = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "expected_rate": Decimal("75"),
    }

    consultant = make_consultant()
    service.repo.create.return_value = consultant
    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock()
    service.db.refresh = AsyncMock()

    result = await service.create_consultant(payload, current_user_id=10)

    assert result is consultant
    service.repo.create.assert_called_once()

    create_kwargs = service.repo.create.call_args.kwargs
    assert create_kwargs["recruiter_id"] == 10
    assert create_kwargs["created_by"] == 10
    assert create_kwargs["marketing_status"] == MarketingStatus.NEW
    assert create_kwargs["availability_status"] == AvailabilityStatus.AVAILABLE_NOW

    service.db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_consultant_duplicate_email(service):
    service.repo.exists_by_email.return_value = True

    payload = MagicMock()
    payload.email = "existing@example.com"
    payload.expected_rate = Decimal("75")

    with pytest.raises(AppException) as exc:
        await service.create_consultant(payload, current_user_id=10)

    assert exc.value.status_code == 400
    assert "Email is already registered" in exc.value.message
    service.repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_consultant_negative_expected_rate(service):
    payload = MagicMock()
    payload.email = "john@example.com"
    payload.expected_rate = Decimal("-1")

    with pytest.raises(AppException) as exc:
        await service.create_consultant(payload, current_user_id=10)

    assert exc.value.status_code == 400
    assert "cannot be negative" in exc.value.message
    service.repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_consultant_rolls_back_on_failure(service):
    payload = MagicMock()
    payload.email = "john@example.com"
    payload.expected_rate = Decimal("75")
    payload.model_dump.return_value = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "expected_rate": Decimal("75"),
    }

    service.repo.create.side_effect = RuntimeError("database failure")

    with pytest.raises(RuntimeError):
        await service.create_consultant(payload, current_user_id=10)

    service.db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# Get consultant / history
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_consultant_success(service):
    consultant = make_consultant()
    service.repo.get_by_public_id.return_value = consultant

    result = await service.get_consultant(consultant.public_id)

    assert result is consultant
    service.repo.get_by_public_id.assert_awaited_once_with(
        consultant.public_id,
        eager_load_recruiter=True,
    )


@pytest.mark.asyncio
async def test_get_consultant_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.get_consultant("missing")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_marketing_history_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.get_marketing_history("missing")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_marketing_history_success(service):
    consultant = make_consultant()

    history_1 = MagicMock()
    history_2 = MagicMock()

    service.repo.get_by_public_id.return_value = consultant

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = [
        history_1,
        history_2,
    ]
    service.db.execute.return_value = result_proxy

    result = await service.get_marketing_history(consultant.public_id)

    assert result == [history_1, history_2]
    service.db.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# List consultants
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_consultants_delegates_to_repository(service):
    pagination = MagicMock()
    sort = MagicMock()

    filters = MagicMock()
    filters.visa_status = "H1B"
    filters.search = "John"

    expected = (["consultant"], MagicMock())
    service.repo.list_paginated.return_value = expected

    result = await service.list_consultants(
        pagination=pagination,
        sort=sort,
        filters=filters,
    )

    assert result == expected
    service.repo.list_paginated.assert_awaited_once()

    kwargs = service.repo.list_paginated.call_args.kwargs
    assert kwargs["pagination_params"] is pagination
    assert kwargs["sort_params"] is sort
    assert kwargs["filter_params"].visa_status == "H1B"
    assert kwargs["filter_params"].search == "John"


# ---------------------------------------------------------------------------
# Update consultant
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_consultant_success(service):
    consultant = make_consultant()

    service.repo.get_by_public_id.return_value = consultant

    payload = MagicMock()
    payload.model_dump.return_value = {
        "first_name": "Updated",
        "phone": "8888888888",
    }

    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock()
    service.db.refresh = AsyncMock()

    result = await service.update_consultant(
        consultant.public_id,
        payload,
        current_user_id=20,
    )

    assert result is consultant
    assert consultant.first_name == "Updated"
    assert consultant.phone == "8888888888"
    assert consultant.updated_by == 20

    service.db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_consultant_not_found(service):
    service.repo.get_by_public_id.return_value = None

    payload = MagicMock()
    payload.model_dump.return_value = {}

    with pytest.raises(AppException) as exc:
        await service.update_consultant(
            "missing",
            payload,
            current_user_id=20,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_consultant_duplicate_email(service):
    consultant = make_consultant(email="old@example.com")
    service.repo.get_by_public_id.return_value = consultant
    service.repo.exists_by_email.return_value = True

    payload = MagicMock()
    payload.model_dump.return_value = {
        "email": "new@example.com",
    }

    with pytest.raises(AppException) as exc:
        await service.update_consultant(
            consultant.public_id,
            payload,
            current_user_id=20,
        )

    assert exc.value.status_code == 400
    assert "Email is already registered" in exc.value.message


@pytest.mark.asyncio
async def test_update_consultant_blocks_status_changes(service):
    consultant = make_consultant()
    service.repo.get_by_public_id.return_value = consultant

    payload = MagicMock()
    payload.model_dump.return_value = {
        "marketing_status": MarketingStatus.MARKETING_ACTIVE,
        "availability_status": AvailabilityStatus.NOT_AVAILABLE,
        "first_name": "Updated",
    }

    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock()
    service.db.refresh = AsyncMock()

    await service.update_consultant(
        consultant.public_id,
        payload,
        current_user_id=20,
    )

    assert consultant.marketing_status == MarketingStatus.NEW
    assert consultant.availability_status == AvailabilityStatus.AVAILABLE_NOW
    assert consultant.first_name == "Updated"


@pytest.mark.asyncio
async def test_update_consultant_rolls_back_on_commit_failure(service):
    consultant = make_consultant()
    service.repo.get_by_public_id.return_value = consultant

    payload = MagicMock()
    payload.model_dump.return_value = {
        "first_name": "Updated",
    }

    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock(side_effect=RuntimeError("commit failed"))

    with pytest.raises(RuntimeError):
        await service.update_consultant(
            consultant.public_id,
            payload,
            current_user_id=20,
        )

    service.db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# Archive consultant
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_archive_consultant_success(service):
    consultant = make_consultant()
    service.repo.get_by_public_id.return_value = consultant

    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock()

    await service.archive_consultant(
        consultant.public_id,
        current_user_id=30,
    )

    assert consultant.deleted_at is not None
    service.db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_consultant_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.archive_consultant(
            "missing",
            current_user_id=30,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_archive_consultant_rolls_back_on_failure(service):
    consultant = make_consultant()
    service.repo.get_by_public_id.return_value = consultant

    service.db.flush = AsyncMock(side_effect=RuntimeError("flush failed"))

    with pytest.raises(RuntimeError):
        await service.archive_consultant(
            consultant.public_id,
            current_user_id=30,
        )

    service.db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# Marketing FSM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transition_marketing_status_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.transition_marketing_status(
            "missing",
            MarketingStatus.READY_FOR_MARKETING,
            changed_by_user_id=10,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_transition_marketing_status_same_status_is_noop(service):
    consultant = make_consultant(
        marketing_status=MarketingStatus.NEW,
    )
    service.repo.get_by_public_id.return_value = consultant

    result = await service.transition_marketing_status(
        consultant.public_id,
        MarketingStatus.NEW,
        changed_by_user_id=10,
    )

    assert result is consultant
    service.db.execute.assert_not_awaited()
    service.db.commit.assert_not_awaited()
    service.audit_service.write_audit_entry.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_marketing_status_invalid_transition(service):
    consultant = make_consultant(
        marketing_status=MarketingStatus.NEW,
    )
    service.repo.get_by_public_id.return_value = consultant

    with pytest.raises(AppException) as exc:
        await service.transition_marketing_status(
            consultant.public_id,
            MarketingStatus.MARKETING_ACTIVE,
            changed_by_user_id=10,
        )

    assert exc.value.status_code == 400
    assert "Invalid state transition" in exc.value.message


@pytest.mark.asyncio
async def test_transition_marketing_status_ready_for_marketing(service):
    consultant = make_consultant(
        marketing_status=MarketingStatus.NEW,
        availability_status=AvailabilityStatus.AVAILABLE_NOW,
    )
    service.repo.get_by_public_id.return_value = consultant

    service.db.execute = AsyncMock()
    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock()
    service.db.refresh = AsyncMock()

    result = await service.transition_marketing_status(
        consultant.public_id,
        MarketingStatus.READY_FOR_MARKETING,
        changed_by_user_id=10,
        reason="Profile verified",
        notes="Ready for marketing",
    )

    assert result is consultant
    assert consultant.marketing_status == MarketingStatus.READY_FOR_MARKETING
    assert consultant.availability_status == AvailabilityStatus.AVAILABLE_NOW
    assert consultant.availability_date == date.today()
    assert consultant.updated_by == 10

    service.db.execute.assert_awaited_once()
    service.db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_transition_marketing_status_not_available(service):
    consultant = make_consultant(
        marketing_status=MarketingStatus.NEW,
    )
    service.repo.get_by_public_id.return_value = consultant

    service.db.execute = AsyncMock()
    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock()
    service.db.refresh = AsyncMock()

    await service.transition_marketing_status(
        consultant.public_id,
        MarketingStatus.PLACED,
        changed_by_user_id=10,
    )

    assert consultant.marketing_status == MarketingStatus.PLACED
    assert consultant.availability_status == AvailabilityStatus.NOT_AVAILABLE
    assert consultant.availability_date is None


@pytest.mark.asyncio
async def test_transition_marketing_status_commit_false(service):
    consultant = make_consultant(
        marketing_status=MarketingStatus.NEW,
    )
    service.repo.get_by_public_id.return_value = consultant

    service.db.execute = AsyncMock()
    service.db.flush = AsyncMock()
    service.db.commit = AsyncMock()
    service.db.refresh = AsyncMock()

    result = await service.transition_marketing_status(
        consultant.public_id,
        MarketingStatus.READY_FOR_MARKETING,
        changed_by_user_id=10,
        commit=False,
    )

    assert result is consultant
    service.db.flush.assert_awaited_once()
    service.db.commit.assert_not_awaited()
    service.db.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_marketing_status_rolls_back_on_failure(service):
    consultant = make_consultant(
        marketing_status=MarketingStatus.NEW,
    )
    service.repo.get_by_public_id.return_value = consultant

    service.db.execute = AsyncMock(side_effect=RuntimeError("db failure"))

    with pytest.raises(RuntimeError):
        await service.transition_marketing_status(
            consultant.public_id,
            MarketingStatus.READY_FOR_MARKETING,
            changed_by_user_id=10,
        )

    service.db.rollback.assert_awaited_once()