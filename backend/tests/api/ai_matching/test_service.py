import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from app.ai_matching.service import AIMatchingService
from app.ai_matching.schemas import BatchMatchRequest


def make_service():
    db = MagicMock()
    db.commit = AsyncMock()

    service = AIMatchingService(db)
    service.repository = MagicMock()
    service.repository.db = db
    return service


def make_requirement():
    return SimpleNamespace(
        id=1,
        public_id=UUID("11111111-1111-1111-1111-111111111111"),
        job_title="Python Developer",
        job_code="PY-001",
        experience_min=3,
        location="Hyderabad",
        technologies=[],
    )


def make_consultant(
    consultant_id=1,
    public_id="22222222-2222-2222-2222-222222222222",
    first_name="John",
    last_name="Doe",
    experience=5,
    location="Hyderabad",
):
    return SimpleNamespace(
        id=consultant_id,
        public_id=UUID(public_id),
        first_name=first_name,
        last_name=last_name,
        total_experience_years=experience,
        current_location=location,
        technologies=[],
    )


@pytest.mark.asyncio
async def test_batch_match_requirement_not_found():
    db = MagicMock()
    service = AIMatchingService(db)

    service.repository.get_requirement = AsyncMock(return_value=None)

    request = BatchMatchRequest(
        requirement_id="00000000-0000-0000-0000-000000000000"
    )

    with pytest.raises(ValueError, match="Requirement not found"):
        await service.batch_match(request)


@pytest.mark.asyncio
async def test_batch_match_no_consultants():
    db = MagicMock()
    service = AIMatchingService(db)

    requirement = MagicMock()
    requirement.experience_min = 3
    requirement.location = "Dallas"
    requirement.technologies = []

    service.repository.get_requirement = AsyncMock(return_value=requirement)
    service.repository.get_all_consultants = AsyncMock(return_value=[])
    service.repository.db.commit = AsyncMock()

    request = BatchMatchRequest(
        requirement_id="00000000-0000-0000-0000-000000000000"
    )

    result = await service.batch_match(request)

    assert result.matches == []
    service.repository.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_history_empty():
    db = MagicMock()
    service = AIMatchingService(db)

    service.repository.get_match_history = AsyncMock(return_value=[])

    result = await service.get_history()

    assert result.history == []


@pytest.mark.asyncio
async def test_batch_match_builds_and_sorts_matches():
    service = make_service()

    requirement = make_requirement()

    consultant_1 = make_consultant(
        consultant_id=1,
        public_id="22222222-2222-2222-2222-222222222222",
        first_name="John",
        last_name="Doe",
    )

    consultant_2 = make_consultant(
        consultant_id=2,
        public_id="33333333-3333-3333-3333-333333333333",
        first_name="Jane",
        last_name="Smith",
    )

    service.repository.get_requirement = AsyncMock(
        return_value=requirement
    )

    service.repository.get_all_consultants = AsyncMock(
        return_value=[consultant_1, consultant_2]
    )

    service.repository.create_match_history = AsyncMock()

    request = BatchMatchRequest(
        requirement_id=requirement.public_id
    )

    with patch(
        "app.ai_matching.service.extract_requirement_technology_names",
        return_value=["python"],
    ), patch(
        "app.ai_matching.service.extract_consultant_technology_names",
        side_effect=[["python"], []],
    ), patch(
        "app.ai_matching.service.calculate_skill_score",
        side_effect=[
            (100, ["python"], []),
            (0, [], ["python"]),
        ],
    ), patch(
        "app.ai_matching.service.calculate_experience_score",
        side_effect=[100, 50],
    ), patch(
        "app.ai_matching.service.calculate_location_score",
        return_value=100,
    ), patch(
        "app.ai_matching.service.calculate_final_match_score",
        side_effect=[100, 50],
    ):

        response = await service.batch_match(request)

    assert len(response.matches) == 2

    assert response.matches[0].score == 100
    assert response.matches[0].recommendation == "Excellent Match"

    assert response.matches[1].score == 50
    assert response.matches[1].recommendation == "Average Match"

    assert service.repository.create_match_history.await_count == 2
    service.repository.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_batch_match_good_match_recommendation():
    service = make_service()

    requirement = make_requirement()
    consultant = make_consultant()

    service.repository.get_requirement = AsyncMock(
        return_value=requirement
    )

    service.repository.get_all_consultants = AsyncMock(
        return_value=[consultant]
    )

    service.repository.create_match_history = AsyncMock()

    request = BatchMatchRequest(
        requirement_id=requirement.public_id
    )

    with patch(
        "app.ai_matching.service.extract_requirement_technology_names",
        return_value=[],
    ), patch(
        "app.ai_matching.service.extract_consultant_technology_names",
        return_value=[],
    ), patch(
        "app.ai_matching.service.calculate_skill_score",
        return_value=(0, [], []),
    ), patch(
        "app.ai_matching.service.calculate_experience_score",
        return_value=0,
    ), patch(
        "app.ai_matching.service.calculate_location_score",
        return_value=0,
    ), patch(
        "app.ai_matching.service.calculate_final_match_score",
        return_value=70,
    ):

        response = await service.batch_match(request)

    assert response.matches[0].recommendation == "Good Match"


@pytest.mark.asyncio
async def test_batch_match_poor_match_recommendation():
    service = make_service()

    requirement = make_requirement()
    consultant = make_consultant()

    service.repository.get_requirement = AsyncMock(
        return_value=requirement
    )

    service.repository.get_all_consultants = AsyncMock(
        return_value=[consultant]
    )

    service.repository.create_match_history = AsyncMock()

    request = BatchMatchRequest(
        requirement_id=requirement.public_id
    )

    with patch(
        "app.ai_matching.service.extract_requirement_technology_names",
        return_value=[],
    ), patch(
        "app.ai_matching.service.extract_consultant_technology_names",
        return_value=[],
    ), patch(
        "app.ai_matching.service.calculate_skill_score",
        return_value=(0, [], []),
    ), patch(
        "app.ai_matching.service.calculate_experience_score",
        return_value=0,
    ), patch(
        "app.ai_matching.service.calculate_location_score",
        return_value=0,
    ), patch(
        "app.ai_matching.service.calculate_final_match_score",
        return_value=20,
    ):

        response = await service.batch_match(request)

    assert response.matches[0].recommendation == "Poor Match"


@pytest.mark.asyncio
async def test_get_history_with_job_code():
    service = make_service()

    record = SimpleNamespace(
        consultant=make_consultant(),
        requirement=make_requirement(),
        match_score=85,
        recommendation="Excellent Match",
        matched_at="2026-09-18T10:00:00",
    )

    service.repository.get_match_history = AsyncMock(
        return_value=[record]
    )

    response = await service.get_history()

    assert len(response.history) == 1
    assert response.history[0].consultant_name == "John Doe"
    assert (
        response.history[0].requirement_name
        == "Python Developer — PY-001"
    )
    assert response.history[0].match_score == 85


@pytest.mark.asyncio
async def test_get_history_without_job_code():
    service = make_service()

    requirement = make_requirement()
    requirement.job_code = None

    record = SimpleNamespace(
        consultant=make_consultant(),
        requirement=requirement,
        match_score=70,
        recommendation="Good Match",
        matched_at="2026-09-18T10:00:00",
    )

    service.repository.get_match_history = AsyncMock(
        return_value=[record]
    )

    response = await service.get_history()

    assert response.history[0].requirement_name == "Python Developer"