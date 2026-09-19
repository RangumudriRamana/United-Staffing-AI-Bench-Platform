from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.requirements.enums import RequirementStatus
from app.requirements.service import RequirementService
from app.consultants.enums import DocumentType


def make_requirement(
    *,
    public_id=None,
    requirement_id=1,
    status=RequirementStatus.DRAFT,
):
    requirement = MagicMock()
    requirement.id = requirement_id
    requirement.public_id = public_id or uuid4()
    requirement.status = status
    requirement.owner_recruiter_id = 10
    requirement.technologies = []
    requirement.documents = []
    requirement.job_code = "REQ-001"
    return requirement


@pytest.fixture
def service():
    db = AsyncMock()
    svc = RequirementService(db)

    svc.repo = MagicMock()
    svc.repo.get_by_public_id = AsyncMock()
    svc.repo.list_requirements_paginated = AsyncMock()

    return svc


# ---------------------------------------------------------------------------
# create_requirement
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_requirement_without_job_code(service):
    payload = {
        "job_title": "Java Developer",
        "job_code": None,
        "rate_min": 70,
        "rate_max": 90,
    }

    requirement = make_requirement()
    service.repo.create.return_value = requirement
    service.repo.get_by_public_id.return_value = requirement

    result = await service.create_requirement(payload, current_user_id=10)

    assert result is requirement
    assert payload["owner_recruiter_id"] == 10
    assert payload["status"] == RequirementStatus.DRAFT
    assert payload["received_date"] is not None

    service.repo.create.assert_called_once()
    service.db.flush.assert_awaited_once()
    service.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_requirement_reload_failure(service):
    payload = {
        "job_title": "Java Developer",
        "job_code": "REQ-RELOAD-001",
        "rate_min": 70,
        "rate_max": 90,
    }

    requirement = make_requirement()
    service.repo.create.return_value = requirement
    service.repo.get_by_public_id.return_value = None
    service.db.scalar.return_value = None

    with pytest.raises(AppException) as exc:
        await service.create_requirement(payload, current_user_id=10)

    assert exc.value.status_code == 404
    assert "after creation" in exc.value.message
    service.db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_requirement_rolls_back_on_repository_failure(service):
    payload = {
        "job_title": "Java Developer",
        "job_code": "REQ-FAIL-001",
        "rate_min": 70,
        "rate_max": 90,
    }

    service.db.scalar.return_value = None
    service.repo.create.side_effect = RuntimeError("database failure")

    with pytest.raises(RuntimeError):
        await service.create_requirement(payload, current_user_id=10)

    service.db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# transition_requirement_status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transition_requirement_valid_status(service):
    requirement = make_requirement(status=RequirementStatus.OPEN)
    service.repo.get_by_public_id.side_effect = [
        requirement,
        requirement,
    ]

    service.db.execute = AsyncMock()
    service.db.commit = AsyncMock()

    result = await service.transition_requirement_status(
        requirement.public_id,
        RequirementStatus.SOURCING,
        user_id=20,
        reason="Sourcing started",
        notes="Begin candidate sourcing",
    )

    assert result is requirement
    assert requirement.status == RequirementStatus.SOURCING

    service.db.execute.assert_awaited_once()
    service.db.commit.assert_awaited_once()

    assert service.repo.get_by_public_id.await_count == 2


@pytest.mark.asyncio
async def test_transition_requirement_same_status_reloads_details(service):
    requirement = make_requirement(status=RequirementStatus.DRAFT)
    refreshed = make_requirement(status=RequirementStatus.DRAFT)

    service.repo.get_by_public_id.side_effect = [
        requirement,
        refreshed,
    ]

    result = await service.transition_requirement_status(
        requirement.public_id,
        RequirementStatus.DRAFT,
        user_id=20,
    )

    assert result is refreshed
    service.db.commit.assert_not_awaited()
    service.db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_requirement_same_status_reload_failure(service):
    requirement = make_requirement(status=RequirementStatus.DRAFT)

    service.repo.get_by_public_id.side_effect = [
        requirement,
        None,
    ]

    with pytest.raises(AppException) as exc:
        await service.transition_requirement_status(
            requirement.public_id,
            RequirementStatus.DRAFT,
            user_id=20,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_transition_requirement_reload_failure_after_commit(service):
    requirement = make_requirement(status=RequirementStatus.DRAFT)

    service.repo.get_by_public_id.side_effect = [
        requirement,
        None,
    ]

    service.db.execute = AsyncMock()
    service.db.commit = AsyncMock()

    with pytest.raises(AppException) as exc:
        await service.transition_requirement_status(
            requirement.public_id,
            RequirementStatus.OPEN,
            user_id=20,
        )

    assert exc.value.status_code == 404
    service.db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_transition_requirement_rolls_back_on_database_failure(service):
    requirement = make_requirement(status=RequirementStatus.DRAFT)
    service.repo.get_by_public_id.return_value = requirement

    service.db.execute = AsyncMock(
        side_effect=RuntimeError("database failure")
    )

    with pytest.raises(RuntimeError):
        await service.transition_requirement_status(
            requirement.public_id,
            RequirementStatus.OPEN,
            user_id=20,
        )

    service.db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# assign_technology
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_assign_technology_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.assign_technology(
            uuid4(),
            technology_id=1,
            minimum_years=3,
            mandatory=True,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_assign_technology_duplicate(service):
    requirement = make_requirement()

    existing_tech = MagicMock()
    existing_tech.technology_id = 5
    requirement.technologies = [existing_tech]

    service.repo.get_by_public_id.return_value = requirement

    with pytest.raises(AppException) as exc:
        await service.assign_technology(
            requirement.public_id,
            technology_id=5,
            minimum_years=3,
            mandatory=True,
        )

    assert exc.value.status_code == 400
    assert "already mapped" in exc.value.message
    service.db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_assign_technology_success(service):
    requirement = make_requirement()

    service.repo.get_by_public_id.return_value = requirement

    result = await service.assign_technology(
        requirement.public_id,
        technology_id=5,
        minimum_years=4,
        mandatory=True,
        notes="Core skill",
    )

    assert result.requirement_id == requirement.id
    assert result.technology_id == 5
    assert result.minimum_years == 4
    assert result.mandatory is True
    assert result.notes == "Core skill"

    service.db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# assign_required_document
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_assign_required_document_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.assign_required_document(
            uuid4(),
            DocumentType.RESUME,
            mandatory=True,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_assign_required_document_duplicate(service):
    requirement = make_requirement()

    existing_doc = MagicMock()
    existing_doc.document_type = DocumentType.RESUME
    requirement.documents = [existing_doc]

    service.repo.get_by_public_id.return_value = requirement

    with pytest.raises(AppException) as exc:
        await service.assign_required_document(
            requirement.public_id,
            DocumentType.RESUME,
            mandatory=True,
        )

    assert exc.value.status_code == 400
    assert "already linked" in exc.value.message
    service.db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_assign_required_document_success(service):
    requirement = make_requirement()
    service.repo.get_by_public_id.return_value = requirement

    result = await service.assign_required_document(
        requirement.public_id,
        DocumentType.RESUME,
        mandatory=True,
        notes="Required document",
    )

    assert result.requirement_id == requirement.id
    assert result.document_type == DocumentType.RESUME
    assert result.mandatory is True
    assert result.notes == "Required document"

    service.db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# reassign_owner
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reassign_owner_success(service):
    requirement = make_requirement()

    refreshed = make_requirement()
    refreshed.owner_recruiter_id = 25

    service.repo.get_by_public_id.side_effect = [
        requirement,
        refreshed,
    ]

    result = await service.reassign_owner(
        requirement.public_id,
        new_owner_id=25,
    )

    assert requirement.owner_recruiter_id == 25
    assert result is refreshed
    service.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reassign_owner_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.reassign_owner(
            uuid4(),
            new_owner_id=25,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_reassign_owner_reload_failure(service):
    requirement = make_requirement()

    service.repo.get_by_public_id.side_effect = [
        requirement,
        None,
    ]

    with pytest.raises(AppException) as exc:
        await service.reassign_owner(
            requirement.public_id,
            new_owner_id=25,
        )

    assert exc.value.status_code == 404
    assert "after owner reassignment" in exc.value.message


# ---------------------------------------------------------------------------
# get_requirement / list_requirements
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_requirement_success(service):
    requirement = make_requirement()
    service.repo.get_by_public_id.return_value = requirement

    result = await service.get_requirement(requirement.public_id)

    assert result is requirement
    service.repo.get_by_public_id.assert_awaited_once_with(
        requirement.public_id,
        eager_load_details=True,
    )


@pytest.mark.asyncio
async def test_get_requirement_not_found(service):
    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.get_requirement(uuid4())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_requirements_delegates_to_repository(service):
    criteria = MagicMock()
    pagination = MagicMock()
    sort = MagicMock()

    expected = (["requirement"], MagicMock())
    service.repo.list_requirements_paginated.return_value = expected

    result = await service.list_requirements(
        criteria,
        pagination,
        sort,
    )

    assert result == expected

    service.repo.list_requirements_paginated.assert_awaited_once_with(
        criteria,
        pagination,
        sort,
    )